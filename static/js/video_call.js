// JS reference to the container where the remote feeds belong
let remoteContainer = document.getElementById("remote-container");
const startButton = document.getElementById("start");
const videoButton = document.getElementById("video-icon");
const micButton = document.getElementById("mic-icon");
var myLocalVideoTrack;
var myLocalAudioTrack;

/**
 * @name addVideoContainer
 * @param uid - uid of the user
 * @description Helper function to add the video stream to "remote-container"
 */
function addVideoContainer(uid){
    let streamDiv=document.createElement("div"); // Create a new div for every stream
    streamDiv.id=uid;                       // Assigning id to div
    streamDiv.style.transform="rotateY(180deg)"; // Takes care of lateral inversion (mirror image)
    remoteContainer.appendChild(streamDiv);      // Add new div to container
}
/**
 * @name removeVideoContainer
 * @param uid - uid of the user
 * @description Helper function to remove the video stream from "remote-container"
 */
function removeVideoContainer (uid) {
    let remDiv=document.getElementById(uid);
    remDiv && remDiv.parentNode.removeChild(remDiv);
}

startButton.onclick = async function () {
    startButton.disabled = true;
    // Client Setup
    // Defines a client for RTC
    const client = AgoraRTC.createClient({ mode: "rtc", codec: "vp8" });

    // Get credentials from the form
    let appId = document.getElementById("app-id").value;
    let channelId = document.getElementById("channel").value;
    let token = document.getElementById("token").value || null;

    // Create local tracks
    const [localAudioTrack, localVideoTrack] = await AgoraRTC.createMicrophoneAndCameraTracks();
    myLocalVideoTrack = localVideoTrack;
    myLocalAudioTrack = localAudioTrack;
    // Initialize the stop button
    initStop(client, localAudioTrack, localVideoTrack);
    
    // Play the local track
    localVideoTrack.play('me');

    // Set up event listeners for remote users publishing or unpublishing tracks
    client.on("user-published", async (user, mediaType) => {
        await client.subscribe(user, mediaType); // subscribe when a user publishes
        if (mediaType === "video") {
          addVideoContainer(String(user.uid)) // uses helper method to add a container for the videoTrack
          user.videoTrack.play(String(user.uid));
        }
        if (mediaType === "audio") {
          user.audioTrack.play(); // audio does not need a DOM element
        }
    });
    client.on("user-unpublished",  async (user, mediaType) => {
        if (mediaType === "video") {
            removeVideoContainer(user.uid) // removes the injected container
            startButton.disabled = false;
        }
    });

    // Join a channnel and retrieve the uid for local user
    const _uid = await client.join(appId, channelId, token, null); 
    await client.publish([localAudioTrack, localVideoTrack]);
    videoButton.disabled = false;
    micButton.disabled = false;
};

function initStop(client, localAudioTrack, localVideoTrack){
    const stopBtn = document.getElementById('stop');
    stopBtn.disabled = false; // Enable the stop button
    stopBtn.onclick = null; // Remove any previous event listener
    stopBtn.onclick = function () {
        client.unpublish(); // stops sending audio & video to agora
        localVideoTrack.stop(); // stops video track and removes the player from DOM
        localVideoTrack.close(); // Releases the resource
        localAudioTrack.stop();  // stops audio track
        localAudioTrack.close(); // Releases the resource
        client.remoteUsers.forEach(user => {
            if (user.hasVideo) {
                removeVideoContainer(user.uid) // Clean up DOM
            }
            client.unsubscribe(user); // unsubscribe from the user
        });
        client.removeAllListeners(); // Clean up the client object to avoid memory leaks
        stopBtn.disabled = true;
        startButton.disabled = false;
        window.location.reload();
    }
}

micButton.onclick = function() {
    if(myLocalAudioTrack == null){
        return;
    }
    if (micButton.firstChild.classList.contains('bi-mic-fill')) {
            myLocalAudioTrack.setEnabled(false);
            console.log("Audio Muted.");
        } else {
            myLocalAudioTrack.setEnabled(true);
            console.log("Audio Unmuted.");
        }
        micButton.firstChild.classList.toggle('bi-mic-fill');
        micButton.firstChild.classList.toggle('bi-mic-mute-fill');
        micButton.classList.toggle('btn-outline-success');
        micButton.classList.toggle('btn-outline-danger');
    }
  
  
// Toggle Video
videoButton.onclick = function(){
    if(myLocalVideoTrack == null){
        return;
    }
    if (videoButton.firstChild.classList.contains('bi-camera-video-fill')) {
        myLocalVideoTrack.setEnabled(false);
        console.log("Video Muted.");
        
    } else {
        myLocalVideoTrack.setEnabled(true);
        console.log("Video Unmuted.");
    }
    videoButton.firstChild.classList.toggle('bi-camera-video-fill');
    videoButton.firstChild.classList.toggle('bi-camera-video-off-fill');
    videoButton.classList.toggle('btn-outline-success');
    videoButton.classList.toggle('btn-outline-danger');
}