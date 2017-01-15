var photo = ['hi'];
var stories = [];
var product_index = 0;
var story_index = 0;

function loadProductPicture(load_photos) {
	window.alert(load_photos);
	photo = load_photos;
}

function loadStoryPicture(load_stories) {
	stories = load_stories;
	if (stories[story_index] != null) {
		$('.product-img').attr("src", stories[index]);
	}
}

$('#product-img').click(function {
	$('#product-img').attr("src", '{{ photos[1] }}');
});

$('.product-img').bind('swiperight', function(){
	if (product_index + 1 < photos.length && photos[product_index + 1] != null) {
		product_index++;
		$('.product-img').attr("src", photos[product_index]);
	}
});

$('.product-img').bind('swipeleft', function(){
	if (product_index - 1 >= 0 && photos[product_index - 1] != null) {
		product_index--;
		$('.product-img').attr("src", photos[product_index-1]);
	}
});

$('.story-img').bind('swiperight', function(){
	if (story_index + 1 < stories.length && photos[story_index + 1] != null) {
		story_index++;
		$('.story-img').attr("src", photos[story_index]);
	}
});

$('.story-img').bind('swipeleft', function(){
	if (story_index - 1 >= 0 && stories[story_index - 1] != null) {
		story_index--;
		$('.story-img').attr("src", photos[story_index]);
	}
});

function test() {
	$('#product-img').attr("src", '{{ photos[1] }}');
}
