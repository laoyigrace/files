<div id="gg">
	<div class="close"><a href="javascript:void(0)" onclick="$('#gg').slideUp('slow');" title="关闭">×</a>
	<div class="bulletin">
		<ul>
			<?php 
				$loop = new WP_Query( array( 'post_type' => 'post','orderby' => 'rand', 'posts_per_page' => get_option('ygj_bulletin_n') ) );
				while ( $loop->have_posts() ) : $loop->the_post();
			?>
			<li><a href="<?php the_permalink(); ?>" title="<?php the_title(); ?>"><?php  _e('随机推荐：《','Three');the_title(); _e('》-(阅读','Three'); the_views();_e('次 |','Three');comments_popup_link( '<span class="leave-reply">' . __( '暂无评论)', 'Three' ) . '</span>', __( '评论1条)', 'Three' ), __( '评论%条)', 'Three' ) );?></a></li>
			<?php endwhile; ?>
		</ul>
	</div>
</div>
<script type="text/javascript">
 // 关闭
function turnoff(obj){
document.getElementById(obj).style.display="none";
}
 // 文字滚动
    (function($){
    $.fn.extend({
    Scroll:function(opt,callback){
    if(!opt) var opt={};
    var _this=this.eq(0).find("ul:first");
    var        lineH=_this.find("li:first").height(),
    line=opt.line?parseInt(opt.line,10):parseInt(this.height()/lineH,10),
    speed=opt.speed?parseInt(opt.speed,10):7000, //卷动速度，数值越大，速度越慢（毫秒）
    timer=opt.timer?parseInt(opt.timer,10):7000; //滚动的时间间隔（毫秒）
    if(line==0) line=1;
    var upHeight=0-line*lineH;
    scrollUp=function(){
    _this.animate({
    marginTop:upHeight
    },speed,function(){
    for(i=1;i<=line;i++){
    _this.find("li:first").appendTo(_this);
    }
    _this.css({marginTop:0});
    });
    }
    _this.hover(function(){
    clearInterval(timerID);
    },function(){
    timerID=setInterval("scrollUp()",timer);
    }).mouseout();
    }
    })
    })(jQuery);
    $(document).ready(function(){
    $(".bulletin").Scroll({line:1,speed:1000,timer:5000});//修改此数字调整滚动时间
    });
</script>