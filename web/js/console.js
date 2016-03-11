var webConsole = function (firstName) {
  
  this.start = function(){
        this.getConfig()
        this.getStatus()

    };
    
  this.getConfig  = function() {
    $.getJSON('/api/get_conf', function(json)
    {
        var error = json.error;
        if (error == undefined){
            var i = 0;
            var len = json.queue.length;
            var table = document.getElementById("tbl");
            var new_table = document.createElement('tbl');
            table.parentNode.replaceChild(new_table, table)
            var tblBody = document.createElement("tbody");
            for (;i < len; i++){
                var curr = json.queue[i];
                
                if (curr.pipe == 1)
                {
                    
                } else {
                
                }
              
                
            }
        }
    });
  };
  
  this.getStatus = function(){
    result = $.getJSON('/api/status', function(json)
    {
        var result = json.status;
        if (result == true) {
            document.getElementById("led").src = "img/str.png";
        } else {
            document.getElementById("led").src = "img/stp.png";
        }
        
        return result;
    });
    
    return result;
  };
  
  this.doStartStop = function(){
    var curr = this.getStatus();
    alert(curr)
    if (curr == true){
            $.getJSON('/api/stop');
        } else {
            $.getJSON('/api/start');
        }
    this.getStatus();
  };
  
    
  
};


var console = new webConsole();