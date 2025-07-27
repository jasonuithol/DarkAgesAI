import { Modal, Button, Text, Loader, Group, Center } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import axios from 'axios';
import { useState, useEffect } from "react";

export function IntroModal({ onBegin, apiEndpoint }) {
  const [opened, { close }] = useDisclosure(true); // starts open
  const [message, setMessage] = useState("");

  useEffect(() => {
    axios.get(apiEndpoint)
      .then((response) => setMessage(response.data))
      .catch((error) => console.error("Error:", error));
  }, [apiEndpoint]);

  const beginAdventure = () => {
    close();     // 🟣 hides the modal
    onBegin();   // 🟢 tells App.js to show MainLayout
  };

  return (
    <Modal
      opened={opened}
      onClose={close}
      centered
      withCloseButton={false}
      fullScreen // 🧱 takes full screen
      title={
        <Text
          size="xl"
          weight={700}
          style={{
            color: '#ffe066', // soft gold
            fontFamily: "'Cinzel', serif",
            textAlign: 'center',
            textShadow: '0 0 8px rgba(255, 230, 100, 0.4)',
          }}
        >
          Your Adventure Begins
        </Text>
      }
      overlayProps={{ opacity: 0.85, blur: 4 }}
      styles={{
        content: {
          backgroundImage: "url('/parchment-texture.png')",
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundColor: "#000", // fallback black
          borderRadius: 0,
          padding: '3rem',
        },
        header: {
          background: 'transparent',
          paddingBottom: '1rem',
        },
      }}
      transitionProps={{
        transition: 'fade',
        duration: 400,
        timingFunction: 'ease',
      }}
    >
      {message ? (
        <Text
          size="lg"
          style={{
            color: '#ccc', // light text on dark
            fontFamily: 'Georgia, serif',
            textAlign: 'left',
            lineHeight: 1.6,
          }}
        >
          {message}
        </Text>
      ) : (
        <Group position="center" mt="md">
          <Loader color="violet" variant="bars" />
        </Group>
      )}

      <Center mt="xl">
          <Button
              radius="xl"
              size="md"
              onClick={beginAdventure}
              styles={{
                root: {
                  fontWeight: 'bold',
                  fontFamily: "'Cinzel', serif",
                  letterSpacing: '1px',
                  background: 'linear-gradient(to right, #5a5a5a, #7c6f5f)', // ⛓️ iron & stone
                  color: '#f0e6c8', // 📜 faded parchment gold
                  textTransform: 'uppercase',
                  boxShadow: '0 0 16px rgba(120, 100, 70, 0.5)',
                  border: '2px solid #8a7d72',
                  transition: 'transform 0.2s ease',
                },
                rootHovered: {
                  transform: 'scale(1.05)',
                  background: 'linear-gradient(to right, #7c6f5f, #a89c84)', // hover glow
                },
              }}
            >
              🛡️ Begin Your Quest
         </Button>
      </Center>

    </Modal>
  );
}
