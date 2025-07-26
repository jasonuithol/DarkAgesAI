import React, { useState } from 'react';
import { IntroModal } from './IntroModal';
import { MainLayout } from './MainLayout';

function App() {
  const [showIntro, setShowIntro] = useState(true);

  // This will be passed to IntroModal to close it
  const handleBegin = () => setShowIntro(false);

  return (
    <>
      {showIntro ? (
        <IntroModal onBegin={handleBegin} apiEndpoint="http://localhost/api"/>
      ) : (
        <MainLayout
          apiEndpoint="http://localhost/api/location"
        />
      )}
    </>
  );
}

export default App;
