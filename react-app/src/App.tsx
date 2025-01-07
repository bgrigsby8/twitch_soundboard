import React, { useEffect, useState } from 'react';
import { Howl } from 'howler';
import soundMappings from './soundMappings.json';
import { Box, Button, Typography } from '@mui/material';
import { io } from 'socket.io-client';

type Sound = {
  name: string;
  sound: Howl;
};

async function fetchSocketToken() {
  const streamlabsAccessToken = "95ab256d5a4f3f32d19dd129ea904bfa1c62f5d1";
  const response = await fetch('http://10.1.11.76:5000/socket/token', {
    headers: {
      Authorization: "Bearer " + streamlabsAccessToken
    }
  })
  console.log("response", response)

  if (!response.ok) {
    throw new Error("Failed to fetch socket token")
  }

  const data = await response.json();
  return data.socketToken;
}

//const socket = new WebSocket(`ws:/127.0.0.1:59650`);

// socket.onopen = () => {
//   console.log("WebSocket connected");

//   // Authenticate
//   const authMessage = {
//     jsonrpc: "2.0",
//     id: 1,
//     method: "auth",
//     params: { resource: "TcpServerService", args: ["95ab256d5a4f3f32d19dd129ea904bfa1c62f5d1"] },
//   };

//   socket.send(JSON.stringify(authMessage));
// };

// socket.onmessage = (event) => {
//   console.log("Message from server:", event.data);
// };

// socket.onerror = (error) => {
//   console.error("WebSocket error:", error);
// }

// socket.onclose = () => {
//   console.log("WebSocket connection closed");
// };


const App: React.FC = () => {
  const [sounds, setSounds] = useState<Sound[]>([]);
  const [currentSound, setCurrentSound] = useState<Sound | null>(null); // Track the currently playing sound

  // const socketToken = fetchSocketToken();
  // console.log("socketToken", socketToken)
  
  // useEffect(() => {
  //   const connectToStreamlabs = () => {
  //     const apiToken = "b66927e7ebabff7eb055a6f746c77f21b2c53941"; // Replace with the token from Streamlabs Desktop
  //     const socket = io(`ws://127.0.0.1:59650`, {
  //       query: { token: apiToken }, // Send the API token as a query parameter
  //       transports: ["websocket"],
  //     });

  //     socket.on("connect", () => {
  //       console.log("Connected to Streamlabs WebSocket");
  //     });

  //     socket.on("disconnect", () => {
  //       console.log("Disconnected from Streamlabs WebSocket");
  //     });

  //     socket.on("event", (eventData) => {
  //       console.log("Streamlabs Event Received:", eventData);

  //       // Example: Handle donation events
  //       if (eventData.type === "donation") {
  //         console.log("Donation received:", eventData.message);
  //       }
  //     });

  //     socket.on("error", (error) => {
  //       console.error("WebSocket error:", error);
  //     });
  //   };

  //   connectToStreamlabs();
  // }, []);

  // useEffect(() => {
  //   const connectToStreamlabs = async () => {
  //     try {
  //       const socketToken = await fetchSocketToken(); // Fetch the token
  //       const streamlabs = io(`https://sockets.streamlabs.com?token=${socketToken}`, {
  //         transports: ["websocket"],
  //       });
  //       console.log("streamlabs", streamlabs)

  //       // // Listen for events
  //       // streamlabs.on("event", (eventData) => {
  //       //   console.log("Streamlabs Event Received:", eventData);

  //       //   if (!eventData.for && eventData.type === "donation") {
  //       //     console.log("Donation Received:", eventData.message);
  //       //   }

  //       //   if (eventData.for === "twitch_account") {
  //       //     switch (eventData.type) {
  //       //       case "follow":
  //       //         console.log("New Twitch Follower:", eventData.message);
  //       //         break;
  //       //       case "subscription":
  //       //         console.log("New Twitch Subscriber:", eventData.message);
  //       //         break;
  //       //       default:
  //       //         console.log("Other Twitch Event:", eventData.message);
  //       //     }
  //       //   }
  //       // });
  //     } catch (error) {
  //       console.error("Error connecting to Streamlabs WebSocket:", error);
  //     }
  //   };

  //   connectToStreamlabs();
  // }, []);

  // const socketToken = fetchSocketToken();
  // console.log("socketToken", socketToken)

  // //const socketUrl = "https://sockets.streamlabs.com/?token=" + socketToken;
  // const streamlabs = new WebSocket(`https://sockets.streamlabs.com?token=` + socketToken);
  // console.log("streamlabs", streamlabs)

  useEffect(() => {
    const loadedSounds = soundMappings.map((mapping: { name: string; file: string }) => ({
      name: mapping.name,
      sound: new Howl({
        src: [`/src/sounds/${mapping.file}`],
        onend: () => {
          setCurrentSound(null); // Clear the current sound when it finishes playing
        }
      }),
    }));
    setSounds(loadedSounds);
  }, []);

  const playSound = (sound: Sound) => {
    if (currentSound) {
      currentSound.sound.stop(); // Stop any currently playing sound
    }
    sound.sound.play();
    setCurrentSound(sound); // Set the current sound
  };

  const stopSound = () => {
    if (currentSound) {
      currentSound.sound.stop(); // Stop the current sound
      setCurrentSound(null); // Clear the current sound
    }
  };

  // const sendGifOverlay = () => {
  //   ws.send(
  //     JSON.stringify({
  //       jsonrpc: "2.0",
  //       method: "showOverlay",
  //       params: {
  //         resource: "GIFOverlay",
  //         data: {
  //           url: "example.com/your-gif.gif",
  //           duration: 5000,
  //         }
  //       }
  //     })
  //   )
  // }

  return (
    <Box sx={{ padding: 4 }}>
      <Typography variant="h3" align="center" gutterBottom>
        Jake's Soundboard
      </Typography>

      {/*Just to add some space between the title and the buttons */}
      <Box sx={{ marginBottom: 10 }}>
        {/* Current Playing Section */}
        {currentSound && (
          <Box
            sx={{
              marginTop: 4,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <Typography variant="h6">
              Now Playing: <strong>{currentSound.name}</strong>
            </Typography>
            <Button variant="contained" color="secondary" onClick={stopSound}>
              Stop
            </Button>
          </Box>
        )}
      </Box>

      {/* Responsive Grid */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)', // 3 columns
          gap: 2, // Space between buttons
          width: '100%',
          maxWidth: '1000px', // Optional: Limit the max width of the grid
          margin: '0 auto', // Center the grid
        }}
      >
        {sounds.map((sound: Sound) => (
          <Button
            key={sound.name}
            variant="contained"
            onClick={() => playSound(sound)}
            sx={{
              aspectRatio: '1', // Makes the button a square
              width: '100%', // Ensures buttons stretch within the grid cell
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: "whitesmoke",
              backgroundColor: "#228B22"
            }}
          >
            {sound.name}
          </Button>
        ))}
        {/* <Button onClick={sendGifOverlay}>Send Gif Overlay</Button> */}
      </Box>
    </Box>
  );
};

export default App;

