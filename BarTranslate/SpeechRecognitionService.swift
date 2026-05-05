//
//  SpeechRecognitionService.swift
//  BarTranslate
//
//  Native speech recognition using SFSpeechRecognizer.
//

import Foundation
import Speech
import AppKit

class SpeechRecognitionService: ObservableObject {
    @Published private(set) var isListening = false
    @Published private(set) var latestTranscript: String = ""

    private var speechRecognizer: SFSpeechRecognizer?
    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?
    private var audioEngine: AVAudioEngine?

    var onPartialResult: ((String) -> Void)?
    var onFinalResult: ((String) -> Void)?
    var onListeningChanged: ((Bool) -> Void)?

    init() {
        speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
    }

    func toggleListening() {
        if isListening {
            stopListening()
        } else {
            startListening()
        }
    }

    func startListening() {
        guard !isListening else { return }

        latestTranscript = ""
        let speechStatus = SFSpeechRecognizer.authorizationStatus()

        switch speechStatus {
        case .authorized:
            checkMicAndStart()
        case .notDetermined:
            SFSpeechRecognizer.requestAuthorization { [weak self] status in
                DispatchQueue.main.async {
                    if status == .authorized {
                        self?.checkMicAndStart()
                    }
                }
            }
        default:
            break
        }
    }

    private func checkMicAndStart() {
        if #available(macOS 14.0, *) {
            let micPerm = AVAudioApplication.shared.recordPermission
            switch micPerm {
            case .granted:
                beginRecording()
            case .undetermined:
                AVAudioApplication.requestRecordPermission { [weak self] granted in
                    DispatchQueue.main.async {
                        if granted {
                            self?.beginRecording()
                        }
                    }
                }
            default:
                break
            }
        } else {
            beginRecording()
        }
    }

    func stopListening() {
        guard isListening else { return }
        let finalText = latestTranscript
        endRecording(sendFinalResult: false, cancelTask: true)

        if !finalText.isEmpty {
            onFinalResult?(finalText)
        }
    }

    private func beginRecording() {
        teardown()

        guard let recognizer = speechRecognizer, recognizer.isAvailable else { return }

        let engine = AVAudioEngine()
        audioEngine = engine

        let inputNode = engine.inputNode
        let recordingFormat = inputNode.outputFormat(forBus: 0)

        let request = SFSpeechAudioBufferRecognitionRequest()
        recognitionRequest = request
        request.shouldReportPartialResults = true
        request.requiresOnDeviceRecognition = false

        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { [weak self] buffer, _ in
            self?.recognitionRequest?.append(buffer)
        }

        do {
            engine.prepare()
            try engine.start()
        } catch {
            teardown()
            return
        }

        setListening(true)

        recognitionTask = recognizer.recognitionTask(with: request) { [weak self] result, error in
            guard let self else { return }

            if error != nil {
                DispatchQueue.main.async {
                    self.endRecording(sendFinalResult: false, cancelTask: true)
                }
                return
            }

            guard let result else { return }

            let text = result.bestTranscription.formattedString
            DispatchQueue.main.async {
                if !text.isEmpty {
                    self.latestTranscript = text
                    self.onPartialResult?(text)
                }

                if result.isFinal {
                    self.endRecording(sendFinalResult: false, cancelTask: false)
                    if !text.isEmpty {
                        self.onFinalResult?(text)
                    }
                }
            }
        }
    }

    private func endRecording(sendFinalResult: Bool, cancelTask: Bool) {
        let finalText = latestTranscript

        stopAudioCapture(cancelTask: cancelTask)
        setListening(false)

        if sendFinalResult && !finalText.isEmpty {
            onFinalResult?(finalText)
        }
    }

    private func teardown() {
        stopAudioCapture(cancelTask: true)
        setListening(false)
    }

    private func stopAudioCapture(cancelTask: Bool) {
        recognitionRequest?.endAudio()
        if cancelTask {
            recognitionTask?.cancel()
        } else {
            recognitionTask?.finish()
        }
        audioEngine?.inputNode.removeTap(onBus: 0)
        audioEngine?.stop()
        audioEngine?.pause()
        audioEngine?.reset()

        recognitionRequest = nil
        recognitionTask = nil
        audioEngine = nil
    }

    private func setListening(_ listening: Bool) {
        guard isListening != listening else { return }
        isListening = listening
        onListeningChanged?(listening)
    }
}
