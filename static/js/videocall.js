$(document).ready(function(){
    var isVideoOn = true;
    let record = false;
    let namespace = "/test";
    let video = document.querySelector("#videoElement");
    let canvas = document.querySelector("#canvasElement");
    let ctx = canvas.getContext('2d');
    photo = document.getElementById('photo');
    var localMediaStream = null;
  console.log(location.port)
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
   
    socket.emit('connect')
  
    socket.on('connect', function() {
      console.log('Connected!');
    });
  
    socket.emit('join_room', {'username': 'abhiraj kale', 'room': 'abhiraj'});
  
    socket.on('join_room_response', function(data){
      console.log(data)
    })
  
    var img = new Image();
  
  
    socket.on('out-image-event',function(data){
      dataURL = data.image_data
      img.src = dataURL
      photo.setAttribute('src', data.image_data);
    });
  
    socket.on('words', function(data){
      console.log(data)
    })
  
    window.addEventListener('beforeunload', function (e) {
      e.preventDefault();
      socket.emit('leave_room', {'username': 'abhiraj kale', 'room': 'abhiraj'})
      e.returnValue = '';
    });
  
    function sendSnapshot() {
      if (!localMediaStream) {
        return;
      }
      
      ctx.drawImage(video, 0, 0, video.videoWidth, video.videoHeight, 0, 0, 300, 150);
  
      let dataURL = canvas.toDataURL('image/jpeg');
      // if(isVideoOn)
        socket.emit('input image', {'room': 'abhiraj', 'dataurl': dataURL, 'record':record});
  
      // socket.emit('output image')
    }
  
   
  
    var constraints = {
      video: {
        width: { min: 380 },
        height: { min: 180 }
      }
    };
  
    navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
      video.srcObject = stream;
      localMediaStream = stream;
  
      setInterval(function () {
        sendSnapshot();
      }, 60);
    }).catch(function(error) {
      console.log(error);
    });
  
  //Buttons Colour change
  function buttonClickHandler() {
    
    console.log(`Button ${this.id} was clicked`);
    if(this.style.backgroundColor != "red")
    {
        this.style.backgroundColor = "red";
    }
    else
    {
        this.style.backgroundColor = '#fff';
    }
  }
  
  const buttons = document.querySelectorAll('button');
  buttons.forEach(button => {
    button.addEventListener('click', buttonClickHandler);
  });
  
  //Buttons Functionality
  const videoToggle = document.getElementById('video-toggle');
  const videoIcon = document.getElementById('video-icon');
  const localVideo = document.getElementById('videoElement');
  const endCallButton = document.getElementById('endCall');
  const muteButton = document.getElementById('mute');
  const signCaptureButton = document.getElementById('signCapture');
  
  let isMuted = false;
  
  
  
  
  //Video Toggle
  videoToggle.addEventListener('click', () => {
    if (isVideoOn) {
      localVideo.srcObject.getTracks()[0].enabled = false;
      videoIcon.classList.remove('fa-video');
      videoIcon.classList.add('fa-video-slash');
    } else {
      localVideo.srcObject.getTracks()[0].enabled = true;
      videoIcon.classList.remove('fa-video-slash');
      videoIcon.classList.add('fa-video');
    }
    isVideoOn = !isVideoOn;
  });
  
  //Mic Toggle
  muteButton.addEventListener('click', () => {
    isMuted = !isMuted;
    const localStream = window.localStream;
    const audioTracks = localStream.getAudioTracks();
    audioTracks.forEach((track) => {
      track.enabled = !isMuted;
    });
    
    // Change button icon based on mute status
    if (isMuted) {
      muteButton.innerHTML = '<i class="fa-solid fa-microphone-slash"></i>';
    } else {
      muteButton.innerHTML = '<i class="fa-solid fa-microphone"></i>';
    }
  });
  
  //End Call
  endCallButton.addEventListener('click', function() {
    window.location.href = "http://www.google.com";
    
  });
  
  signCaptureButton.addEventListener('click', function(){
    if(record) record = false;
    else record = true;
  })
  
  //Sign-Language-Button
  
  // import io from 'socket.io-client';
  
  // // Initialize socket connection
  // const socket = io('http://localhost:3000');
  
  // // Get reference to the "signCapture" button
  // const signCaptureButton = document.getElementById('signCapture');
  
  // let buttonState = false;
  
  // // Add click event listener to the button
  // signCaptureButton.addEventListener('click', () => {
  
  //   buttonState = !buttonState;
    
  //   if (buttonState) {
  //     // Emit "signCaptureOn" event if button is turned on
  //     socket.emit('signCaptureOn');
  //     signCaptureButton.classList.add('active');
  //   } else {
  //     // Emit "signCaptureOff" event if button is turned off
  //     socket.emit('signCaptureOff');
  //     signCaptureButton.classList.remove('active');
  //   }
  // });
  
  
  
  });