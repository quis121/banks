package com.mobileshop;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends AppCompatActivity {
    
    private EditText usernameEditText;
    private EditText passwordEditText;
    private Button loginButton;
    private ProgressBar loadingProgressBar;
    private TextView statusTextView;
    private ApiService apiService;
    private ExecutorService executorService;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        // Initialize views
        initializeViews();
        
        // Initialize API service and executor
        apiService = new ApiService();
        executorService = Executors.newSingleThreadExecutor();
        
        // Set up login button click listener
        loginButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                performLogin();
            }
        });
    }
    
    private void initializeViews() {
        usernameEditText = findViewById(R.id.usernameEditText);
        passwordEditText = findViewById(R.id.passwordEditText);
        loginButton = findViewById(R.id.loginButton);
        loadingProgressBar = findViewById(R.id.loadingProgressBar);
        statusTextView = findViewById(R.id.statusTextView);
    }
    
    private void performLogin() {
        String username = usernameEditText.getText().toString().trim();
        String password = passwordEditText.getText().toString().trim();
        
        // Validate input
        if (username.isEmpty() || password.isEmpty()) {
            showMessage("Please enter both username and password");
            return;
        }
        
        // Show loading state
        setLoadingState(true);
        
        // Perform login in background thread
        executorService.execute(new Runnable() {
            @Override
            public void run() {
                try {
                    LoginRequest loginRequest = new LoginRequest(username, password);
                    LoginResponse response = apiService.login(loginRequest);
                    
                    // Update UI on main thread
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            setLoadingState(false);
                            handleLoginResponse(response);
                        }
                    });
                    
                } catch (Exception e) {
                    // Handle error on main thread
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            setLoadingState(false);
                            showMessage("Network error: " + e.getMessage());
                        }
                    });
                }
            }
        });
    }
    
    private void handleLoginResponse(LoginResponse response) {
        if (response != null && response.isSuccess()) {
            showMessage("Login successful! Welcome, " + response.getUser().getUsername());
            statusTextView.setText("Logged in as: " + response.getUser().getUsername());
            statusTextView.setVisibility(View.VISIBLE);
            
            // Here you would typically navigate to the main app screen
            // For now, we'll just show a success message
            
        } else {
            String message = response != null ? response.getMessage() : "Login failed";
            showMessage(message);
        }
    }
    
    private void setLoadingState(boolean isLoading) {
        if (isLoading) {
            loginButton.setEnabled(false);
            loadingProgressBar.setVisibility(View.VISIBLE);
            statusTextView.setText("Logging in...");
            statusTextView.setVisibility(View.VISIBLE);
        } else {
            loginButton.setEnabled(true);
            loadingProgressBar.setVisibility(View.GONE);
        }
    }
    
    private void showMessage(String message) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show();
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (executorService != null) {
            executorService.shutdown();
        }
    }
}

