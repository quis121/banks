package com.mobileshop;

import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

public class ApiService {
    
    // Change this to your actual API URL
    // For local testing, use your computer's IP address instead of localhost
    // Example: "http://192.168.1.100:5000/api"
    private static final String BASE_URL = "http://10.0.2.2:5000/api"; // Android emulator localhost
    private static final String LOGIN_ENDPOINT = "/login";
    
    public LoginResponse login(LoginRequest loginRequest) throws Exception {
        URL url = new URL(BASE_URL + LOGIN_ENDPOINT);
        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
        
        try {
            // Set up the connection
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setRequestProperty("Accept", "application/json");
            connection.setDoOutput(true);
            connection.setConnectTimeout(10000); // 10 seconds
            connection.setReadTimeout(10000); // 10 seconds
            
            // Create JSON payload
            JSONObject jsonPayload = new JSONObject();
            jsonPayload.put("username", loginRequest.getUsername());
            jsonPayload.put("password", loginRequest.getPassword());
            
            // Send the request
            try (OutputStream os = connection.getOutputStream()) {
                byte[] input = jsonPayload.toString().getBytes(StandardCharsets.UTF_8);
                os.write(input, 0, input.length);
            }
            
            // Get the response
            int responseCode = connection.getResponseCode();
            
            BufferedReader reader;
            if (responseCode >= 200 && responseCode < 300) {
                reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
            } else {
                reader = new BufferedReader(new InputStreamReader(connection.getErrorStream()));
            }
            
            StringBuilder response = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                response.append(line);
            }
            reader.close();
            
            // Parse the response
            return parseLoginResponse(response.toString());
            
        } finally {
            connection.disconnect();
        }
    }
    
    private LoginResponse parseLoginResponse(String jsonResponse) {
        try {
            JSONObject jsonObject = new JSONObject(jsonResponse);
            
            boolean success = jsonObject.getBoolean("success");
            String message = jsonObject.getString("message");
            
            if (success && jsonObject.has("user")) {
                JSONObject userObject = jsonObject.getJSONObject("user");
                int userId = userObject.getInt("user_id");
                String username = userObject.getString("username");
                
                User user = new User(userId, username);
                
                String token = null;
                if (jsonObject.has("token")) {
                    token = jsonObject.getString("token");
                }
                
                return new LoginResponse(success, message, user, token);
            } else {
                return new LoginResponse(success, message, null, null);
            }
            
        } catch (Exception e) {
            return new LoginResponse(false, "Failed to parse response: " + e.getMessage(), null, null);
        }
    }
}

