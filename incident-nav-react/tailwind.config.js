// tailwind.config.js
module.exports = {
  darkMode: 'class', // Active la gestion du mode sombre via la classe .dark
  content: [
    "./src/**/*.{js,ts,jsx,tsx}", 
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Thème clair
        light: {
          background: '#E5E5E5', // Arrière-plan principal (gris clair)
          surface: '#FFFFFF', // Arrière-plan des cartes et des panneaux
          text: '#1C1C1E', // Couleur du texte principal (noir)
          accent: '#7FBF7F', // Vert Calme pour les boutons/accents
          alert: '#E57373', // Rouge Pâle (erreurs/alertes)
        },
        // Thème sombre
        dark: {
          background: '#1C1C1E', // Arrière-plan principal (noir profond)
          surface: '#2E2E2E', // Arrière-plan des cartes et des panneaux
          text: '#F9F9F9', // Texte blanc sur fond sombre
          accent: '#7FBF7F', // Vert Calme
          alert: '#FF6B6B', // Rouge d'alerte
        },
      },
    },
  },
  plugins: [],
}
