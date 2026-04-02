document.addEventListener("DOMContentLoaded", function () {
    var audio = new Audio();
    var tracks = JSON.parse(document.getElementById("track_data").textContent);
    var current_index = -1;
    var is_playing = false;

    var btn_play = document.getElementById("btn_play");
    var btn_prev = document.getElementById("btn_prev");
    var btn_next = document.getElementById("btn_next");
    var progress_container = document.getElementById("progress_container");
    var progress_bar = document.getElementById("progress_bar");
    var time_current = document.getElementById("time_current");
    var time_total = document.getElementById("time_total");
    var volume_slider = document.getElementById("volume_slider");
    var track_name_display = document.querySelector(".player_track_name");
    var track_items = document.querySelectorAll(".track_item");

    audio.volume = parseFloat(volume_slider.value);

    function format_time(seconds) {
        if (isNaN(seconds) || !isFinite(seconds)) return "0:00";
        var mins = Math.floor(seconds / 60);
        var secs = Math.floor(seconds % 60);
        return mins + ":" + (secs < 10 ? "0" : "") + secs;
    }

    function update_active_track() {
        track_items.forEach(function (item) {
            item.classList.remove("active");
        });
        if (current_index >= 0 && current_index < track_items.length) {
            track_items[current_index].classList.add("active");
        }
    }

    function load_track(index) {
        if (index < 0 || index >= tracks.length) return;
        current_index = index;
        audio.src = tracks[index].file;
        track_name_display.textContent = tracks[index].name;
        progress_bar.style.width = "0%";
        time_current.textContent = "0:00";
        time_total.textContent = "0:00";
        update_active_track();
    }

    function toggle_play() {
        if (current_index === -1 && tracks.length > 0) {
            load_track(0);
        }
        if (is_playing) {
            audio.pause();
            is_playing = false;
            btn_play.textContent = "play";
        } else {
            audio.play();
            is_playing = true;
            btn_play.textContent = "pause";
        }
    }

    function play_next() {
        if (current_index < tracks.length - 1) {
            load_track(current_index + 1);
            audio.play();
            is_playing = true;
            btn_play.textContent = "pause";
        } else {
            audio.pause();
            is_playing = false;
            btn_play.textContent = "play";
        }
    }

    function play_prev() {
        if (audio.currentTime > 3 && current_index >= 0) {
            audio.currentTime = 0;
        } else if (current_index > 0) {
            load_track(current_index - 1);
            audio.play();
            is_playing = true;
            btn_play.textContent = "pause";
        }
    }

    btn_play.addEventListener("click", toggle_play);
    btn_next.addEventListener("click", play_next);
    btn_prev.addEventListener("click", play_prev);

    audio.addEventListener("timeupdate", function () {
        if (audio.duration) {
            var percent = (audio.currentTime / audio.duration) * 100;
            progress_bar.style.width = percent + "%";
            time_current.textContent = format_time(audio.currentTime);
            time_total.textContent = format_time(audio.duration);
        }
    });

    audio.addEventListener("ended", function () {
        play_next();
    });

    audio.addEventListener("error", function () {
        if (current_index < tracks.length - 1) {
            play_next();
        }
    });

    progress_container.addEventListener("click", function (e) {
        if (!audio.duration) return;
        var rect = progress_container.getBoundingClientRect();
        var ratio = (e.clientX - rect.left) / rect.width;
        audio.currentTime = ratio * audio.duration;
    });

    volume_slider.addEventListener("input", function () {
        audio.volume = parseFloat(volume_slider.value);
    });

    track_items.forEach(function (item) {
        item.addEventListener("click", function () {
            var index = parseInt(item.getAttribute("data-index"), 10);
            load_track(index);
            audio.play();
            is_playing = true;
            btn_play.textContent = "pause";
        });
    });
});
