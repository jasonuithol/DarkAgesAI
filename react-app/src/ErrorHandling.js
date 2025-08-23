// TODO: load the earthEatingDemon.png and base64 encode it.
export async function loadImageToBase64(path) {
  const res = await fetch(path);
  const blob = await res.blob();
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result); // data:image/png;base64,...
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

export async function earthEatingDemon(level, incantation) {
    const earthEatingDemonSrc = await loadImageToBase64('/TheDemonOfHTTP500.png')
    if (!earthEatingDemonSrc) {
        throw new Error('Demon missing in action');
    }
    return {
        name: 'An error occurred and now a demon is eating everything',
        description: `You hear an incantation from deep beneath the earth "${incantation}" and a level ${level} demon erupts from the core of the planet and starts devouring everything in this particular location.`,
        image: earthEatingDemonSrc
    };
}

