const ros = new ROSLIB.Ros();

ros.on('error', function(error) {
  console.error('Error connecting to ROS: ', error);
});

ros.connect('ws://localhost:9090');

var compressedImageTopic = new ROSLIB.Topic({
    ros: ros,
    name : '/compressed_image_topic_2',
    messageType : 'sensor_msgs/CompressedImage'
});

compressedImageTopic.subscribe(function(message) {
    var imageData = "data:image/jpeg;base64," + message.data;
    var image = new Image();
    image.src = imageData;
    image.onload = function() {
        var canvas = document.getElementById("canvas");
        canvas.width = 1200; 
        canvas.height = 720; 
        if(canvas) {
            var context = canvas.getContext("2d");
            context.drawImage(image, 0, 0);
        }
    };
});

var topic = new ROSLIB.Topic({
    ros : ros,
    name : '/modKontrolu',
    messageType : 'std_msgs/String'
});

var message = new ROSLIB.Message({
    data : '-1'
});
topic.publish(message);

var kontrol=-1;
var manuelSurusButton = document.getElementById("manuelSurusButton");
manuelSurusButton.addEventListener("click", function() {

    if(kontrol!=-2){
        if (manuelSurusButton.classList.contains("clicked1")) {
            manuelSurusButton.classList.remove("clicked1");
            manuelSurusButton.classList.add("clicked2");
            manuelSurusButton.classList.remove("clicked3");
        } 
        else if (manuelSurusButton.classList.contains("clicked2")) {
            manuelSurusButton.classList.remove("clicked1");
            manuelSurusButton.classList.remove("clicked2");
            manuelSurusButton.classList.add("clicked3");
        } 
        else if (manuelSurusButton.classList.contains("clicked3")) {
            manuelSurusButton.classList.remove("clicked1");
            manuelSurusButton.classList.remove("clicked2");
            manuelSurusButton.classList.remove("clicked3");
        } 
        else {
            manuelSurusButton.classList.add("clicked1");
        }
    }

    if(kontrol==0){
        var message = new ROSLIB.Message({
            data : '1'
        });
        topic.publish(message);
        kontrol=1;
    }
    else if(kontrol==1){
        var message = new ROSLIB.Message({
            data : '2'
        });
        topic.publish(message);
        kontrol=2;
    }
    else if(kontrol==2){
        var message = new ROSLIB.Message({
            data : '-1'
        });
        topic.publish(message);
        kontrol=-1;
    }
    else if(kontrol==-1){
        var message = new ROSLIB.Message({
            data : '0'
        });
        topic.publish(message);
        kontrol=0;
    }
    
});

var twistTopic = new ROSLIB.Topic({
    ros: ros,
    name: '/cmd_vel1',
    messageType: 'geometry_msgs/Twist'
});

var newTwistTopic = new ROSLIB.Topic({
    ros: ros,
    name : '/cmd_vel',
    messageType : 'geometry_msgs/Twist'
});

val_linear_x = 0
val_angular_z = 0

newTwistTopic.subscribe(function(message) {
    val_linear_x = message.linear.x
    val_angular_z = message.angular.z
});

var acilDurdurma = document.getElementById("acilDurdurma");
acilDurdurma.addEventListener("click", function() {
    var twist = new ROSLIB.Message({
        linear : {
            x : 0
        },
        angular : {
            z : 0
        }
    });
    twistTopic.publish(twist)
    kontrol=-2;
    manuelSurusButton.classList.remove("clicked1");
    manuelSurusButton.classList.remove("clicked2");
    manuelSurusButton.classList.remove("clicked3");
    if (acilDurdurma.classList.contains("clicked")) {
        acilDurdurma.classList.remove("clicked");
        kontrol=-1;
    } 
    else {
        acilDurdurma.classList.add("clicked");
    }
    if (kontrol==-1){
        var message = new ROSLIB.Message({
            data : '-1'
        });
    }
    if (kontrol==-2){
        var message = new ROSLIB.Message({
            data : '-2'
        });
    }
    topic.publish(message);
});

var ileriButton = document.getElementById("ileriButton");
var sagButton = document.getElementById("sagButton");
var solButton = document.getElementById("solButton");
var geriButton = document.getElementById("geriButton");
var durButton = document.getElementById("durButton");

ileriButton.addEventListener("click", function() {
    if(kontrol==1){
        val_linear_x +=0.02
        var twist = new ROSLIB.Message({
            linear : {
                x : val_linear_x
            },
            angular : {
                z : val_angular_z
            }
        });
        twistTopic.publish(twist)
    }
});

sagButton.addEventListener("click", function() {
    if(kontrol==1){
        val_angular_z -=0.02
        var twist = new ROSLIB.Message({
            linear : {
                x : val_linear_x
            },
            angular : {
                z : val_angular_z
            }
        });
        twistTopic.publish(twist)
    }
});

solButton.addEventListener("click", function() {
    if(kontrol==1){
        val_angular_z +=0.02
        var twist = new ROSLIB.Message({
            linear : {
                x : val_linear_x
            },
            angular : {
                z : val_angular_z
            }
        });
        twistTopic.publish(twist)
    }
});

geriButton.addEventListener("click", function() {
    if(kontrol==1){
        val_linear_x -= 0.02
        var twist = new ROSLIB.Message({
            linear : {
                x : val_linear_x
            },
            angular : {
                z : val_angular_z
            }
        });
        twistTopic.publish(twist)
    }
});

durButton.addEventListener("click", function() {
    if(kontrol==1){
        var twist = new ROSLIB.Message({
            linear : {
                x : 0
            },
            angular : {
                z : 0
            }
        });
        twistTopic.publish(twist)
   }
});