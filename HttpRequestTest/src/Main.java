import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.ProtocolException;
import java.net.URL;
import java.nio.charset.StandardCharsets;


public class Main {

    private static HttpURLConnection connection;

    public static void main (String[] args) throws IOException {
        BufferedReader reader;
        String line;
        StringBuffer responseContent = new StringBuffer();

        // URL url = new URL("http://127.0.0.1:5000/register");
        URL url = new URL("http://34.89.117.73:5000/register");
        connection = (HttpURLConnection) url.openConnection();

        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "application/json");
        connection.setRequestProperty("Accept", "application/json");
        connection.setDoOutput(true);

        String data = "{\n  \"student_id\": \"s1911022\",\n  \"password\": \"123123\"\n}";
        byte[] out = data.getBytes(StandardCharsets.UTF_8);

        OutputStream stream = connection.getOutputStream();
        stream.write(out);

        System.out.println(connection.getResponseCode() + " " + connection.getResponseMessage());


    }

}
