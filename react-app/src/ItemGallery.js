import { Stack, Loader } from '@mantine/core';
import React, { useState, useEffect, useCallback } from "react";

import { CardWithAction } from './CardWithAction';

export function ItemGallery({ apiEndpoint, actionPostUrl, actionButtonText }) {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchEntries = useCallback(() => {
    setLoading(true);
    fetch(apiEndpoint)
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch data');
        return res.json();
      })
      .then(data => {
        const transformed = data.map(item => ({
          name: item.name,
          description: item.description,
          item_type: item.item_type,
          imageSrc: `data:image/png;base64,${item.image}`
        }));
        setEntries(transformed);
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false)); 
  }, [apiEndpoint]);

  useEffect(() => {
    fetchEntries();
  }, [fetchEntries]);


  if (loading) return <Loader />;
  if (error) return <div>Error: {error}</div>;

  return (
    <Stack>
      {entries.map((entry, index) => (
        <CardWithAction
          key={index}
          entry={entry}
          postUrl={actionPostUrl}
          buttonText={actionButtonText}
          reloadGallery={fetchEntries}
        />
      ))}
    </Stack>
  );
}