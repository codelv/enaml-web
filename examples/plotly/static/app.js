$(document).ready(function(){
    $('.plotly-chart').each(function(i, e){
        Plotly.newPlot(e, $(e).data('traces'), $(e).data('layout')); 
    });
});
