//
//  SpeechRecognitionService.swift
//  BarTranslate
//
//  Native speech recognition using SFSpeechRecognizer to provide
//  voice-to-text input for Google Translate.
//

import Foundation
import Speech
import AppKit

class SpeechRecognitionService: ObservableObject {
    @Published var isListening = false
    @Published var transcript: String = ""

    private var speechRecognizer: SFSpeechRecognizer?
    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?
    private var audioEngine: AVAudioEngine?

    var onResult: ((String) -> Void)?

    init() {
        speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
    }

    func requestAuthorization(completion: @escaping (Bool) -> Void) {
        SFSpeechRecognizer.requestAuthorization { authStatus in
            DispatchQueue.main.async {
                switch authStatus {
                case .authorized:
                    self.requestMicPermission(completion: completion)
                default:
                    print("[SpeechRecognition] Speech recognition not authorized: \(authStatus.rawValue)")
                    completion(false)
                }
            }
        }
    }

    private func requestMicPermission(completion: @escaping (Bool) -> Void) {
        // AVCaptureDevice is available from macOS 10.7+ for checking mic permission
        if #available(macOS 14.0, *) {
            let permission = AVAudioApplication.shared.recordPermission
            switch permission {
            case .granted:
                completion(true)
            case .undetermined:
                AVAudioApplication.requestRecordPermission { granted in
                    DispatchQueue.main.async {
                        completion(granted)
                    }
                }
            default:
                print("[SpeechRecognition] Microphone permission denied")
                completion(false)
            }
        } else {
            // On macOS 13, use AVAudioSession-like approach via TCC
            // SFSpeechRecognizer will trigger the system permission prompt when we start recording
            completion(true)
        }
    }

    func startListening() {
        guard !isListening else { return }

        requestAuthorization { [weak self] authorized in
            guard authorized else { return }
            self?.beginRecording()
        }
    }

    func stopListening() {
        guard isListening else { return }
        endRecording()
    }

    func toggleListening() {
        if isListening {
            stopListening()
        } else {
            startListening()
        }
    }

    private func beginRecording() {
        // Clean up any existing task
        recognitionTask?.cancel()
        recognitionTask = nil

        let engine = AVAudioEngine()
        audioEngine = engine

        let inputNode = engine.inputNode
        let recordingFormat = inputNode.outputFormat(forBus: 0)

        let request = SFSpeechAudioBufferRecognitionRequest()
        recognitionRequest = request
        request.shouldReportPartialResults = true

        guard let recognizer = speechRecognizer, recognizer.isAvailable else {
            print("[SpeechRecognition] Speech recognizer not available")
            return
        }

        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { buffer, _ in
            request.append(buffer)
        }

        engine.prepare()
        do {
            try engine.start()
        } catch {
            print("[SpeechRecognition] Could not start audio engine: \(error)")
            return
        }

        isListening = true
        transcript = ""

        recognitionTask = recognizer.recognitionTask(with: request) { [weak self] result, error in
            guard let self else { return }

            if let result {
                let text = result.bestTranscription.formattedString
                DispatchQueue.main.async {
                    self.transcript = text
                }

                if result.isFinal {
                    DispatchQueue.main.async {
                        self.endRecording()
                        self.onResult?(text)
                    }
                }
            }

            if let error {
                print("[SpeechRecognition] Recognition error: \(error)")
                DispatchQueue.main.async {
                    self.endRecording()
                }
            }
        }
    }

    private func endRecording() {
        audioEngine?.stop()
        audioEngine?.inputNode.removeTap(onBus: 0)
        recognitionRequest?.endAudio()
        recognitionTask?.cancel()

        audioEngine = nil
        recognitionRequest = nil
        recognitionTask = nil

        let finalText = transcript
        isListening = false

        if !finalText.isEmpty {
            onResult?(finalText)
        }
    }
}
