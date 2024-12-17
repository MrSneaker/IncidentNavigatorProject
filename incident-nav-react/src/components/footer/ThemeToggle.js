import React, { useEffect, useState } from 'react';

const ThemeToggle = () => {
  const [theme, setTheme] = useState('light');

  // Charger le thème au montage du composant
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    document.documentElement.classList.add(savedTheme);
  }, []);

  // Fonction pour basculer le thème clair/sombre
  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);

    // Supprime l'ancien thème et ajoute le nouveau
    document.documentElement.classList.remove(theme);
    document.documentElement.classList.add(newTheme);

    // Sauvegarder le thème sélectionné dans le localStorage
    localStorage.setItem('theme', newTheme);
  };

  return (
    <button 
      onClick={toggleTheme} 
      className="flex items-center bg-light-surface dark:bg-dark-surface text-primary-dark dark:text-white border border-neutral p-2 rounded-full shadow-lg transition-all hover:bg-neutral hover:dark:bg-primary-light"
    >
      <span className="mr-2">
        {theme === 'dark' ? '🌞' : '🌙'}
      </span>
      <span className="font-semibold">
        {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
      </span>
    </button>
  );
};

export default ThemeToggle;
