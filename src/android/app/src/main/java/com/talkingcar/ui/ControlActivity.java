package com.talkingcar.ui;

import android.os.AsyncTask;
import android.os.Bundle;
import android.support.design.widget.Snackbar;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.View;
import android.widget.Button;

import com.talkingcar.CommandListener;
import com.talkingcar.R;
import com.talkingcar.SpeechRecognitionListener;

import java.io.File;
import java.io.IOException;

import butterknife.Bind;
import butterknife.ButterKnife;
import butterknife.OnClick;
import edu.cmu.pocketsphinx.Assets;
import edu.cmu.pocketsphinx.SpeechRecognizer;

import static edu.cmu.pocketsphinx.SpeechRecognizerSetup.defaultSetup;

public class ControlActivity extends AppCompatActivity implements CommandListener {

    private static final String TAG = "com.talkingcar";
    private SpeechRecognizer _speechRecognizer;

    @Bind(R.id.toolbar) Toolbar _toolbar;
    @Bind(R.id.record_button) Button _recordButton;

    @Override
    public void onCreate(Bundle state) {
        super.onCreate(state);
        setContentView(R.layout.activity_control);
        ButterKnife.bind(this);

        setSupportActionBar(_toolbar);

        // Recognizer initialization is a time-consuming and it involves IO,
        // so we execute it in async task
        new AsyncTask<Void, Void, Exception>() {
            @Override
            protected Exception doInBackground(Void... params) {
                try {
                    Assets assets = new Assets(ControlActivity.this);
                    File assetDir = assets.syncAssets();
                    setupRecognizer(assetDir);
                } catch (IOException e) {
                    return e;
                }
                return null;
            }

            @Override
            protected void onPostExecute(Exception result) {
                if (result != null) {
                    Log.e(TAG, "Failed to init recognizer", result);
                } else {
                    _speechRecognizer.startListening("commands");
                }
            }
        }.execute();
    }

    private void setupRecognizer(File assetsDir) throws IOException {
        // The recognizer can be configured to perform multiple searches
        // of different kind and switch between them
        _speechRecognizer = defaultSetup()
                .setAcousticModel(new File(assetsDir, "en-us-ptm"))
                .setDictionary(new File(assetsDir, "cmudict-en-us.dict"))
                .setKeywordThreshold(1e-45f)
                .setBoolean("-allphone_ci", true)
                .getRecognizer();

        _speechRecognizer.addListener(new SpeechRecognitionListener(this, _speechRecognizer));

        // Create grammar-based search for selection between demos
        File commandsGrammar = new File(assetsDir, "commands.gram");
        _speechRecognizer.addGrammarSearch("commands", commandsGrammar);
    }

    @Override
    public void onDestroy() {
        super.onDestroy();

        _speechRecognizer.cancel();
        _speechRecognizer.shutdown();
    }

    @Override
    public void onCommand(String command) {
        if (command != null) {
            Snackbar.make(findViewById(android.R.id.content), command, Snackbar.LENGTH_SHORT)
                    .show();
        }

        _speechRecognizer.stop();
        _recordButton.setEnabled(true);

    }

    @OnClick(R.id.record_button)
    public void onRecordButtonClicked(View view) {
        _speechRecognizer.startListening("commands");
        _recordButton.setEnabled(false);
    }
}
