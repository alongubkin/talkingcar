package com.talkingcar;

import android.util.Log;

import edu.cmu.pocketsphinx.Hypothesis;
import edu.cmu.pocketsphinx.RecognitionListener;
import edu.cmu.pocketsphinx.SpeechRecognizer;

public class SpeechRecognitionListener implements RecognitionListener {

    private static final String TAG = "com.talkingcar";

    private CommandListener _commandListener;
    private SpeechRecognizer _speechRecognizer;

    public SpeechRecognitionListener(CommandListener commandListener, SpeechRecognizer speechRecognizer) {
        _commandListener = commandListener;
        _speechRecognizer = speechRecognizer;
    }

    /**
     * In partial result we get quick updates about current hypothesis. In
     * keyword spotting mode we can react here, in other modes we need to wait
     * for final result in onResult.
     */
    @Override
    public void onPartialResult(Hypothesis hypothesis) {
        if (hypothesis == null) {
            return;
        }
    }

    /**
     * This callback is called when we stop the recognizer.
     */
    @Override
    public void onResult(Hypothesis hypothesis) {
        if (hypothesis != null) {
            _commandListener.onCommand(hypothesis.getHypstr());
        }
    }

    @Override
    public void onBeginningOfSpeech() {
    }

    /**
     * We stop recognizer here to get a final result
     */
    @Override
    public void onEndOfSpeech() {
        _commandListener.onCommand(null);
    }

    @Override
    public void onError(Exception error) {
        Log.e(TAG, "SpeechRecognizer error", error);
    }

    @Override
    public void onTimeout() {
    }
}
