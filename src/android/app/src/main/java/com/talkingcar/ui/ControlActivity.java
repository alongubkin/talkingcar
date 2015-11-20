package com.talkingcar.ui;

import android.os.AsyncTask;
import android.os.Bundle;
import android.os.SystemClock;
import android.support.design.widget.Snackbar;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.View;
import android.widget.Button;

import com.talkingcar.CommandBuilder;
import com.talkingcar.CommandListener;
import com.talkingcar.R;
import com.talkingcar.SpeechRecognitionListener;

import java.io.File;
import java.io.IOException;
import java.io.OutputStream;
import java.net.Socket;

import butterknife.Bind;
import butterknife.ButterKnife;
import butterknife.OnClick;
import edu.cmu.pocketsphinx.Assets;
import edu.cmu.pocketsphinx.SpeechRecognizer;

import static edu.cmu.pocketsphinx.SpeechRecognizerSetup.defaultSetup;

public class ControlActivity extends AppCompatActivity implements CommandListener {

    private static final String TAG = "com.talkingcar";

    private static final String CAR_HOST = "192.168.4.1";
    private static final int CAR_PORT = 8763;

    private SpeechRecognizer _speechRecognizer;

    private Socket _client;
    private OutputStream _clientOutputStream;

    @Bind(R.id.toolbar) Toolbar _toolbar;
    @Bind(R.id.record_button) Button _recordButton;
    @Bind(R.id.connecting_container) View _connectingContainer;

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
                }
            }
        }.execute();

        connect();
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

            CommandBuilder builder = new CommandBuilder();

            if (command.equals("forward") || command.equals("go")) {
                sendCommand(builder.gas(CommandBuilder.Gear.FORWARD));
            } else if (command.equals("backward") || command.equals("reverse")) {
                sendCommand(builder.gas(CommandBuilder.Gear.BACKWARD));
            } else if (command.equals("left")) {
                sendCommand(builder.setDirection(CommandBuilder.Direction.LEFT));
            } else if (command.equals("right")) {
                sendCommand(builder.setDirection(CommandBuilder.Direction.RIGHT));
            } else if (command.equals("brake") || command.equals("stop")) {
                sendCommand(builder.brake());
            }
        }

        _speechRecognizer.stop();
        _recordButton.setEnabled(true);
    }

    @OnClick(R.id.record_button)
    public void onRecordButtonClicked(View view) {
        if (_client == null || !_client.isConnected()) {
            connect();
            return;
        }

        _speechRecognizer.startListening("commands");
        _recordButton.setEnabled(false);
    }

    private void connect() {
        if (_client != null && _client.isConnected()) {
            return;
        }

        _connectingContainer.setVisibility(View.VISIBLE);
        _recordButton.setVisibility(View.GONE);

        new AsyncTask<Void, Void, Void>() {

            @Override
            protected Void doInBackground(Void... params) {

                while (_client == null || !_client.isConnected()) {
                    try {
                        _client = new Socket(CAR_HOST, CAR_PORT);
                        _clientOutputStream = _client.getOutputStream();
                    } catch (IOException e) {
                        Log.d(TAG, "Connection failed, trying again.", e);
                        SystemClock.sleep(2000);
                    }
                }

                return null;
            }

            @Override
            protected void onPostExecute(Void params) {
                _connectingContainer.setVisibility(View.GONE);
                _recordButton.setVisibility(View.VISIBLE);
            }

        }.execute();
    }

    private void sendCommand(byte[] command) {
        if (_client == null || !_client.isConnected()) {
            connect();
            return;
        }

        try {
            _clientOutputStream.write(command);
            _clientOutputStream.flush();
        } catch (IOException e) {
            Log.e(TAG, "Cannot send message", e);
        }
    }
}
