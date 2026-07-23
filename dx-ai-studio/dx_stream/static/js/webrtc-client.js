/**
 * DX Stream — WebRTC 클라이언트
 * SDP/ICE 교환 via HTTP POST (WebSocket 미사용)
 * 자동 재시도 (지수 백오프), FPS/latency 통계
 */
DXStream.webrtc = (function() {
    var pc = null;
    var _pollTimer = null;
    var _statsTimer = null;
    var _retryCount = 0;
    var _retryTimeout = null;
    var _videoEl = null;
    var MAX_RETRIES = 5;
    var RETRY_DELAYS = [1000, 2000, 3000, 4000, 5000];
    // 재생 정지(black screen) 감시: getStats 폴링에서 디코딩된 프레임이
    // 연속으로 늘지 않으면 GStreamer 버스 에러 등으로 스트림이 죽은 것으로 간주한다.
    var _errorEl = null;
    var _stallPolls = 0;
    var _lastFramesDecoded = -1;
    var STALL_LIMIT = 3; // 2초 폴링 × 3 = 약 6초간 신규 프레임 없음
    // WebRTC media is peer-to-peer UDP. It connects when the browser can reach the board
    // directly (localhost / same-LAN host candidates). A remote viewer over an SSH tunnel or
    // different subnet only ever sees the board's host (LAN) candidates, which don't route, so
    // ICE sits at "checking" forever and never fires 'failed'. Guard with a hard deadline: if
    // we aren't connected within CONNECT_TIMEOUT, give up and let the caller fall back to MJPEG
    // (which rides the same HTTP proxy and works from anywhere).
    var _onFail = null;
    var _connectTimer = null;
    var _gaveUp = false;
    var CONNECT_TIMEOUT = 9000;

    function _log(msg) { console.log('[WebRTC]', msg); }

    /* ── 지속형 에러 배너: 자동 숨김 없이 스트림 복구/사용자 조작까지 유지 ── */
    function _errorHost() {
        var video = _videoEl || DXStream.$('webrtc-video');
        if (video && video.parentNode) return video.parentNode;
        return DXStream.$('demo-video-section') || document.body;
    }

    function _showError(msg) {
        var host = _errorHost();
        if (!host) return;
        if (host.style && !host.style.position) host.style.position = 'relative';
        var el = _errorEl;
        if (!el || !el.parentNode) {
            el = document.createElement('div');
            el.id = 'webrtc-error';
            el.className = 'webrtc-error-overlay';
            el.style.cssText = 'position:absolute;inset:0;display:flex;flex-direction:column;' +
                'align-items:center;justify-content:center;gap:12px;text-align:center;padding:16px;' +
                'background:rgba(0,0,0,.72);color:#fff;z-index:20;border-radius:8px;';
            host.appendChild(el);
            _errorEl = el;
        }
        // 자동 숨김 타이머 없음 — _clearError() 로만 제거된다.
        el.innerHTML = '';
        var text = document.createElement('div');
        text.className = 'webrtc-error-msg';
        text.style.cssText = 'font-size:14px;max-width:90%;line-height:1.4;';
        text.textContent = msg;
        el.appendChild(text);
        var actions = document.createElement('div');
        actions.className = 'webrtc-error-actions';
        actions.style.cssText = 'display:flex;gap:8px;';
        var retryBtn = document.createElement('button');
        retryBtn.className = 'btn btn-sm btn-primary';
        retryBtn.textContent = T('Retry');
        retryBtn.onclick = function () { DXStream.webrtc.retry(); };
        var dismissBtn = document.createElement('button');
        dismissBtn.className = 'btn btn-sm btn-ghost';
        dismissBtn.textContent = T('Dismiss');
        dismissBtn.onclick = function () { _clearError(); };
        actions.appendChild(retryBtn);
        actions.appendChild(dismissBtn);
        el.appendChild(actions);
        el.style.display = '';
    }

    function _clearError() {
        if (_errorEl && _errorEl.parentNode) _errorEl.parentNode.removeChild(_errorEl);
        _errorEl = null;
    }

    function _payloadTypesFromSdp(sdp) {
        var payloadTypes = {};
        (sdp || '').split(/\r?\n/).forEach(function(line) {
            var match = line.match(/^a=rtpmap:(\d+)\s+([^\/\s]+)/i);
            if (match) payloadTypes[match[2].toUpperCase()] = parseInt(match[1], 10);
        });
        return payloadTypes;
    }

    function preferredPayloadTypes() {
        var probe = new RTCPeerConnection({ iceServers: [] });
        probe.addTransceiver('video', { direction: 'recvonly' });
        return probe.createOffer().then(function(offer) {
            return _payloadTypesFromSdp(offer.sdp);
        }).catch(function(err) {
            _log('payload type preflight failed: ' + err.message);
            return {};
        }).then(function(payloadTypes) {
            probe.close();
            return payloadTypes;
        });
    }

    function connect(videoElement, _isRetry, onFail) {
        if (onFail !== undefined) _onFail = onFail;
        if (!_isRetry) {
            _retryCount = 0;
            _gaveUp = false;
            _clearError();
            // No connect deadline: Local vs Remote is now an explicit user choice, so we don't
            // silently time out WebRTC and switch modes. Remote viewers pick MJPEG up front;
            // WebRTC still falls back only on a genuine connection failure (see _attemptRetry).
        }
        _stallPolls = 0;
        _lastFramesDecoded = -1;
        _videoEl = videoElement;
        if (pc) _cleanup();
        // No STUN: the board is air-gapped so stun.l.google.com is unreachable (onicecandidateerror
        // + wasted gathering time). Host candidates are all that connect here anyway.
        var config = { iceServers: [] };
        pc = new RTCPeerConnection(config);
        pc.addTransceiver('video', { direction: 'recvonly' });
        _log('PeerConnection created');

        pc.ontrack = function(e) {
            _log('ontrack fired, streams=' + (e.streams ? e.streams.length : 0) +
                 ', track.kind=' + (e.track ? e.track.kind : 'null'));
            if (e.streams && e.streams[0]) {
                videoElement.srcObject = e.streams[0];
                videoElement.muted = true;
                videoElement.play().then(function() {
                    _log('video play() OK');
                }).catch(function(err) {
                    _log('video play() failed: ' + err.message);
                });
                _log('srcObject set');
                _stallPolls = 0;
                _clearError(); // 트랙 수신 = 스트림 복구
            } else if (e.track) {
                var stream = new MediaStream();
                stream.addTrack(e.track);
                videoElement.srcObject = stream;
                videoElement.muted = true;
                videoElement.play().catch(function() {});
                _log('srcObject set from track (no streams)');
                _stallPolls = 0;
                _clearError();
            }
        };

        pc.onicecandidate = function(e) {
            if (e.candidate) {
                _log('local ICE: ' + e.candidate.candidate.substring(0, 60));
                DXStream.postJ('/api/webrtc/ice', {
                    sdpMLineIndex: e.candidate.sdpMLineIndex,
                    candidate: e.candidate.candidate,
                });
            }
        };

        pc.oniceconnectionstatechange = function() {
            _log('ICE state: ' + (pc ? pc.iceConnectionState : 'null'));
            if (pc && (pc.iceConnectionState === 'connected' || pc.iceConnectionState === 'completed')) {
                _clearConnectTimer(); // connected in time — cancel the MJPEG-fallback deadline
                _stopICEPoll();
            }
        };

        pc.onconnectionstatechange = function() {
            _log('Connection state: ' + (pc ? pc.connectionState : 'null'));
            if (pc && pc.connectionState === 'failed') {
                DXStream.toast(T('WebRTC connection lost'), 'error');
                _showError(T('WebRTC connection lost'));
                _attemptRetry();
            }
        };

        var offer;
        return pc.createOffer().then(function(o) {
            offer = o;
            return pc.setLocalDescription(offer);
        }).then(function() {
            _log('Offer sent to server');
            return DXStream.postJ('/api/webrtc/offer', { sdp: offer.sdp });
        }).then(function(resp) {
            if (resp.error) {
                DXStream.toast(T('WebRTC connection failed: ') + resp.error, 'error');
                _showError(T('WebRTC connection failed: ') + resp.error);
                _attemptRetry();
                return false;
            }
            _log('Answer received, length=' + (resp.sdp ? resp.sdp.length : 0));
            var answer = new RTCSessionDescription({ type: 'answer', sdp: resp.sdp });
            return pc.setRemoteDescription(answer).then(function() {
                _log('Remote description set');
                _startICEPoll();
                _startStatsPoll();
                return true;
            });
        }).catch(function(err) {
            _log('Error: ' + err.message);
            DXStream.toast(T('WebRTC error: ') + err.message, 'error');
            _showError(T('WebRTC error: ') + err.message);
            _attemptRetry();
            return false;
        });
    }

    function _attemptRetry() {
        _cleanup();
        if (_retryCount < MAX_RETRIES && _videoEl) {
            var delay = RETRY_DELAYS[_retryCount] || 4000;
            _retryCount++;
            DXStream.toast(T('Retrying WebRTC connection… (' + _retryCount + '/' + MAX_RETRIES + ')',
                'WebRTC 재연결 시도 중… (' + _retryCount + '/' + MAX_RETRIES + ')'), 'info');
            _retryTimeout = setTimeout(function () {
                connect(_videoEl, true);
            }, delay);
        } else if (_retryCount >= MAX_RETRIES) {
            _giveUp('retries');
        }
    }

    function _clearConnectTimer() {
        if (_connectTimer) { clearTimeout(_connectTimer); _connectTimer = null; }
    }

    // WebRTC can't connect here (remote/NAT/tunnel — see CONNECT_TIMEOUT). Stop retrying and
    // hand control back to the caller so it can switch this demo to the MJPEG stream.
    function _giveUp(reason) {
        if (_gaveUp) return;
        _gaveUp = true;
        _clearConnectTimer();
        if (_retryTimeout) { clearTimeout(_retryTimeout); _retryTimeout = null; }
        _retryCount = MAX_RETRIES;
        _cleanup();
        _clearError();
        _log('giving up on WebRTC (' + reason + ') — falling back to MJPEG');
        if (typeof _onFail === 'function') _onFail(reason);
    }

    function retry() {
        _retryCount = 0;
        _gaveUp = false;
        _clearError();
        if (_videoEl) connect(_videoEl, false);
    }

    function _startICEPoll() {
        if (_pollTimer) return;
        var _addedCandidates = {};
        _pollTimer = setInterval(function() {
            DXStream.api('/api/webrtc/ice').then(function(candidates) {
                if (Array.isArray(candidates)) {
                    candidates.forEach(function(c) {
                        if (pc && c.candidate) {
                            var key = c.candidate;
                            if (_addedCandidates[key]) return;
                            _addedCandidates[key] = true;
                            _log('remote ICE: ' + key.substring(0, 60));
                            pc.addIceCandidate(new RTCIceCandidate(c)).catch(function() {});
                        }
                    });
                }
            });
        }, 1000);
    }

    function _stopICEPoll() {
        if (_pollTimer) {
            clearInterval(_pollTimer);
            _pollTimer = null;
        }
    }

    function _startStatsPoll() {
        if (_statsTimer) clearInterval(_statsTimer);
        DXStream._statsTimer = _statsTimer = setInterval(function() {
            if (!pc || pc.connectionState !== 'connected') return;
            pc.getStats().then(function(stats) {
                var fps = 0, jitter = 0, packetsLost = 0, rtt = 0, framesDecoded = 0;
                stats.forEach(function(report) {
                    if (report.type === 'inbound-rtp' && report.kind === 'video') {
                        fps = report.framesPerSecond || 0;
                        packetsLost = report.packetsLost || 0;
                        jitter = report.jitter || 0;
                        framesDecoded = report.framesDecoded || 0;
                    }
                    if (report.type === 'candidate-pair' && report.state === 'succeeded') {
                        rtt = report.currentRoundTripTime || 0;
                    }
                });
                // 재생 정지 감시: 연결은 살아있는데 디코딩 프레임이 늘지 않으면
                // (GStreamer 버스 에러 등) 검은 화면이 방치되지 않도록 에러를 노출한다.
                if (framesDecoded === _lastFramesDecoded) {
                    _stallPolls++;
                    if (_stallPolls >= STALL_LIMIT) {
                        _showError(T('Stream stalled — no video frames received. The pipeline may have failed.'));
                    }
                } else {
                    _stallPolls = 0;
                    _clearError(); // 프레임 진행 = 정상 재생
                }
                _lastFramesDecoded = framesDecoded;
                _updateStatsOverlay(fps, rtt, jitter, packetsLost);
            }).catch(function() {});
        }, 2000);
    }

    function _updateStatsOverlay(fps, rtt, jitter, packetsLost) {
        var overlay = DXStream.$('webrtc-stats-overlay');
        if (!overlay) return;
        var lostLabel = {ko:'손실', ja:'ロスト', 'zh-CN':'丢失', 'zh-TW':'遺失'}[DXStream.S.lang] || 'lost';
        overlay.textContent = Math.round(fps) + ' FPS | RTT: ' + (rtt * 1000).toFixed(0) + 'ms | ' + lostLabel + ': ' + packetsLost;
    }

    function _cleanup() {
        _stopICEPoll();
        if (_statsTimer) { clearInterval(_statsTimer); _statsTimer = null; DXStream._statsTimer = null; }
        if (pc) { pc.close(); pc = null; }
    }

    function disconnect() {
        if (_retryTimeout) { clearTimeout(_retryTimeout); _retryTimeout = null; }
        _clearConnectTimer();
        _gaveUp = true; // prevent fallback firing after a deliberate stop
        _retryCount = MAX_RETRIES; // prevent auto-retry after manual disconnect
        _cleanup();
        _clearError();
        var overlay = DXStream.$('webrtc-stats-overlay');
        if (overlay) overlay.textContent = '';
    }

    function isConnected() {
        return pc !== null && pc.connectionState === 'connected';
    }

    return {
        connect: connect,
        disconnect: disconnect,
        isConnected: isConnected,
        retry: retry,
        preferredPayloadTypes: preferredPayloadTypes
    };
})();
if (typeof registerStreamLangRefresher === 'function') {
  registerStreamLangRefresher(function() {
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
    if (typeof DXStream !== 'undefined' && DXStream.S && DXStream.S.currentPage && typeof DXStream.nav === 'function') {
      DXStream.nav(DXStream.S.currentPage);
    }
  });
}
