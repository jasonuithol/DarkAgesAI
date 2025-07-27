import { useEffect, useState } from 'react';
import { Box } from '@mantine/core';
import { IconSword, IconShield } from '@tabler/icons-react';

export const BattleSpinner = () => {
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveIndex((prev) => (prev + 1) % 4);
    }, 300); // tweak speed here

    return () => clearInterval(interval);
  }, []);

  const icons = [IconSword, IconShield, IconShield, IconSword];

  return (
    <Box
      style={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: '120px',
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gridTemplateRows: '1fr 1fr',
        gap: '8px',
      }}
    >
      {icons.map((Icon, index) => (
        <Icon
          key={index}
          size={32}
          style={{
            color: activeIndex === index ? '#888' : '#333',
            textShadow: activeIndex === index ? '0 0 6px #888' : 'none',
            transition: 'color 0.3s ease-in-out',
          }}
        />
      ))}
    </Box>
  );
};

export default BattleSpinner;