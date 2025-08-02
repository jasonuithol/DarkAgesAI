import { Card, Button, Text, Image } from '@mantine/core';
import { useState } from "react";

export function CardWithAction({ entry, postUrl, buttonText, reloadGallery, setAllowedButtons }) {
    const [hovered, setHovered] = useState(false);
    
    const handlePost = async () => {
        const response = await fetch(postUrl, {
            method: 'POST',
            body: entry.name
        });

        if (!response.ok) {
            console.error("Failed to post:", response.statusText);
            return;
        }

        const responseData = await response.json();

        // Extract the allowed_buttons object
        const allowedButtonsData = responseData['allowed_buttons'];

        setAllowedButtons(allowedButtonsData);
        reloadGallery(); // Refresh entries
    };

    return (
        <div
            style={{ position: 'relative' }}
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => setHovered(false)}
        >
            <Card shadow="sm" padding="lg" radius="md" bg="dark.6">
                <Text weight={600} color="gold" size="lg">
                    [{entry.item_type}] {entry.name}
                </Text>
                <Text size="sm" color="dimmed">{entry.description}</Text>
                <Image src={entry.imageSrc} alt={entry.name} fit="contain" mt="md" />
            </Card>
            {hovered && (
                <Button
                    style={{
                        position: 'absolute',
                        top: '50%',
                        left: '50%',
                        transform: 'translate(-50%, -50%)'
                    }}
                    onClick={handlePost}
                >
                    {buttonText}
                </Button>
            )}
        </div>
    );
}

