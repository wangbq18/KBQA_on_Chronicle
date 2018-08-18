/**
 * Created by Dell on 2018/4/4.
 */
   $("#submit").click(function (e) {
       var text = $("#question").val();

       if (text == "") return;

       var url = "/wx?question='" + text + "'";

       $.get (url, function (data, error) {
           $("#answer").text(data);
       });
   });