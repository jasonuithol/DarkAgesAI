import { Button, Text, Loader, Flex, Box, ActionIcon } from '@mantine/core';

export function DirectionalControls({ isMoving, onMove, allowedButtons }) {
    return (
        <Box mt="xl">
            <Flex gap="sm" wrap="wrap">
                {isMoving ? (
                    <>
                        <Loader size="sm" />
                        <Text ml="sm">Loading...</Text>
                    </>
                ) : (
                    <Box mt="xl">
                        <Text size="sm" color="cyan" weight={600} mb="sm">
                            Where shall you go next?
                        </Text>
                        <Flex direction="column" align="center" gap="sm">
                            {/* North */}
                            <Button onClick={() => onMove('n')} disabled={!allowedButtons['n']}>N</Button>

                            {/* Middle row: West, Icon, East */}
                            <Flex gap="sm" align="center">
                                <Button onClick={() => onMove('w')} disabled={!allowedButtons['w']}>W</Button>
                                <ActionIcon size="lg" variant="outline">
                                    <span role="img" aria-label="compass">🧭</span>
                                </ActionIcon>
                                <Button onClick={() => onMove('e')} disabled={!allowedButtons['e']}>E</Button>
                            </Flex>

                            {/* South */}
                            <Button onClick={() => onMove('s')} disabled={!allowedButtons['s']}>S</Button>
                        </Flex>
                    </Box>
                )}
            </Flex>
        </Box>
    );
}