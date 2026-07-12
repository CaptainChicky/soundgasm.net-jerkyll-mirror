// Headless injection payload (hooks + state accumulator),
// Injected via Playwright's add_init_script (runs before any page JS).

(function () {
	"use strict";

	// Cache native refs before anything can tamper
	var _toString = Function.prototype.toString;
	var _call = Function.prototype.call;
	var _apply = Function.prototype.apply;
	var _defProp = Object.defineProperty;

	// Global state, Python reads this via page.evaluate after playback ends
	window.__INTERCEPTOR = {
		chunks: [],
		mimeType: "audio/mp4",
		playerEl: null,
		done: false,       // set true on 'ended' event
		startTime: null,
		error: null,
	};

	// Make hooked fn pass toString() anti-tamper checks
	function spoof(hooked, original) {
		var str = _call.call(_toString, original);
		_defProp(hooked, "toString", {
			value: function () { return str; },
			writable: true,
			configurable: true,
		});
	}

	// ---- HOOK 1: addSourceBuffer -> per-instance appendBuffer hook ----
	try {
		var MS = window.MediaSource || window.ManagedMediaSource;
		if (MS && MS.prototype) {
			var _addSB = MS.prototype.addSourceBuffer;
			var hAddSB = function addSourceBuffer(mime) {
				var sb = _apply.call(_addSB, this, arguments);
				window.__INTERCEPTOR.mimeType = mime;

				try {
					var _append = sb.appendBuffer;
					var hAppend = function appendBuffer(data) {
						try {
							if (!window.__INTERCEPTOR.startTime)
								window.__INTERCEPTOR.startTime = Date.now();

							var buf =
								data instanceof ArrayBuffer
									? data.slice(0)
									: data.buffer.slice(
										data.byteOffset,
										data.byteOffset + data.byteLength
									);
							window.__INTERCEPTOR.chunks.push(new Uint8Array(buf));
						} catch (e) {
							window.__INTERCEPTOR.error = e.message;
						}
						return _apply.call(_append, this, arguments);
					};
					spoof(hAppend, _append);
					_defProp(sb, "appendBuffer", {
						value: hAppend,
						writable: true,
						configurable: true,
					});
				} catch (e) { }
				return sb;
			};
			spoof(hAddSB, _addSB);
			MS.prototype.addSourceBuffer = hAddSB;
		}
	} catch (e) { }

	// ---- HOOK 2: play() to capture <audio>/<video> element ----
	try {
		var _play = HTMLMediaElement.prototype.play;
		var hPlay = function play() {
			if (!window.__INTERCEPTOR.playerEl) {
				window.__INTERCEPTOR.playerEl = this;
			}
			return _apply.call(_play, this, arguments);
		};
		spoof(hPlay, _play);
		HTMLMediaElement.prototype.play = hPlay;
	} catch (e) { }

	// ---- HOOK 3: capture-phase listeners (backup) ----
	document.addEventListener(
		"play",
		function (e) {
			var t = e.target;
			if (
				t &&
				(t.tagName === "AUDIO" || t.tagName === "VIDEO") &&
				!window.__INTERCEPTOR.playerEl
			) {
				window.__INTERCEPTOR.playerEl = t;
			}
		},
		true
	);

	document.addEventListener(
		"ended",
		function (e) {
			var t = e.target;
			if (t && (t.tagName === "AUDIO" || t.tagName === "VIDEO")) {
				window.__INTERCEPTOR.done = true;
			}
		},
		true
	);
})();
