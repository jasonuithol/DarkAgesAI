import { useState } from 'react';
import { IntroScreen } from './IntroScreen';
import { MainLayout } from './MainLayout';

function App() {
  const [showIntro, setShowIntro] = useState(true);

  // This will be passed to IntroScreen to close it
  const handleBegin = () => setShowIntro(false);

  return (
    <>
      {showIntro ? (
        <IntroScreen onBegin={handleBegin} apiEndpoint="http://localhost/api"/>
      ) : (
        <MainLayout
          apiEndpoint="http://localhost/api/location"
        />
      )}
    </>
  );
}

export default App;
