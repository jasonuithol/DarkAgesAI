import { Button, Text, Loader, Group, Center } from '@mantine/core';
import axios from 'axios';
import { useState, useEffect } from "react";

export function IntroScreen({ onBegin, apiEndpoint }) {
    const [message, setMessage] = useState("");

    useEffect(() => {
        axios.get(apiEndpoint)
            .then((response) => setMessage(response.data))
            .catch((error) => console.error("Error:", error));
    }, [apiEndpoint]);

    return (
        <div
            style={{
                position: 'absolute',
                inset: 0,
                backgroundImage: "url('/parchment-texture.png')",
                backgroundSize: "cover",
                backgroundPosition: "center",
                backgroundColor: "#000",
                padding: '3rem',
                zIndex: 1000,
            }}
        >
            <Text
                size="xl"
                weight={700}
                style={{
                    color: '#ffe066',
                    fontFamily: "'Cinzel', serif",
                    textAlign: 'center',
                    textShadow: '0 0 8px rgba(255, 230, 100, 0.4)',
                    marginBottom: '2rem',
                }}
            >
                Your Adventure Begins
            </Text>

            {message ? (
                <Text
                    size="lg"
                    style={{
                        color: '#ccc',
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
                    onClick={onBegin}
                    styles={{
                        root: {
                            fontWeight: 'bold',
                            fontFamily: "'Cinzel', serif",
                            letterSpacing: '1px',
                            background: 'linear-gradient(to right, #5a5a5a, #7c6f5f)',
                            color: '#f0e6c8',
                            textTransform: 'uppercase',
                            boxShadow: '0 0 16px rgba(120, 100, 70, 0.5)',
                            border: '2px solid #8a7d72',
                            transition: 'transform 0.2s ease',
                        },
                        rootHovered: {
                            transform: 'scale(1.05)',
                            background: 'linear-gradient(to right, #7c6f5f, #a89c84)',
                        },
                    }}
                >
                    🛡️ Begin Your Quest
                </Button>
            </Center>
        </div>
    );
}