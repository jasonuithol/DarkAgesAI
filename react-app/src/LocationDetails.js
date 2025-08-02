import { Box, Text, Button, Flex } from '@mantine/core';
import { DirectionalControls } from './DirectionalControls';

export function LocationDetails({
    entry,
    isMoving,
    handleMove,
    galleryParams,
    setGalleryParams,
    allowedButtons
}) {

    function GalleryButton({ label, endpoint, postUrl, buttonText, disabled }) {
        const isActive = galleryParams.apiEndpoint === endpoint;
        return (
            <Button
                onClick={() =>
                    setGalleryParams({
                        apiEndpoint: endpoint,
                        actionPostUrl: postUrl,
                        actionButtonText: buttonText
                    })
                }
                variant={isActive ? "filled" : "light"}
                color={isActive ? "cyan" : "gray"}
                disabled={disabled}
            >
                {label}
            </Button>
        );
    }

    return (
        <Box style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            {/* Title + Description */}
            <Box>
                <Text size="xl" color="cyan" weight={700}>{entry.name}</Text>
                <Text size="md" color="dimmed" mt="md">{entry.description}</Text>
            </Box>

            {/* Spacer pushes controls and buttons downward */}
            <Box style={{ flexGrow: 1 }} />

            {/* Centered Directional Controls */}
            <Box style={{ display: 'flex', justifyContent: 'center' }}>
                <DirectionalControls isMoving={isMoving} onMove={handleMove} allowedButtons={allowedButtons}/>
            </Box>

            {/* Item Toggle Buttons */}
            <Box mt="md" style={{ display: 'flex', justifyContent: 'center' }}>
                <Flex gap="sm">
                    <GalleryButton
                        label="Combat"
                        endpoint="/api/enemies"
                        postUrl="/api/attack"
                        buttonText="Attack"
                        disabled={!allowedButtons['combat']}
                    />
                    <GalleryButton
                        label="Local Items"
                        endpoint="/api/location/items"
                        postUrl="/api/take"
                        buttonText="Take"
                        disabled={!allowedButtons['local_items']}
                    />
                    <GalleryButton
                        label="Inventory"
                        endpoint="/api/inventory"
                        postUrl="/api/drop"
                        buttonText="Drop"
                        disabled={!allowedButtons['inventory']}
                    />
                </Flex>
            </Box>
        </Box>
    );
}