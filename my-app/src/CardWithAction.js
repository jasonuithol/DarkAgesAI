import { Card, Button, Text, Image } from '@mantine/core';
import React, { useState } from "react";

export function CardWithAction({ entry, postUrl, buttonText, reloadGallery }) {
  const [hovered, setHovered] = useState(false);

  const handlePost = async () => {
    await fetch(postUrl, {
      method: 'POST',
      body: entry.name
    });
    reloadGallery(); // Callback to refresh entries
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

