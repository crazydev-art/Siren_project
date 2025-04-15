import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, MapPin, TrendingUp } from 'lucide-react';

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <div className="text-center space-y-6">
        <h1 className="text-5xl font-bold text-gray-900">
          Analysez les entreprises d'
          <span className="bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
            Île-de-France
          </span>
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Accédez à des données détaillées sur les entreprises franciliennes, suivez leur croissance et prenez des décisions éclairées.
        </p>
        <div className="flex justify-center gap-4">
          <button
            onClick={() => navigate('/search')}
            className="px-8 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-all transform hover:scale-105 shadow-lg hover:shadow-xl"
          >
            Commencer la recherche
          </button>
          <button
            onClick={() => navigate('/map')}
            className="px-8 py-3 bg-white text-blue-600 rounded-xl hover:bg-blue-50 transition-all transform hover:scale-105 shadow-lg hover:shadow-xl border border-blue-200"
          >
            Voir la carte
          </button>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid md:grid-cols-3 gap-8">
        <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow">
          <div className="bg-blue-100 w-12 h-12 rounded-xl flex items-center justify-center mb-4">
            <Search className="text-blue-600 w-6 h-6" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Recherche avancée</h3>
          <p className="text-gray-600">
            Trouvez rapidement des entreprises par nom, SIRET, ou secteur d'activité en Île-de-France.
          </p>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow">
          <div className="bg-blue-100 w-12 h-12 rounded-xl flex items-center justify-center mb-4">
            <MapPin className="text-blue-600 w-6 h-6" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Carte interactive</h3>
          <p className="text-gray-600">
            Visualisez la répartition des entreprises par secteur dans toute la région francilienne.
          </p>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow">
          <div className="bg-blue-100 w-12 h-12 rounded-xl flex items-center justify-center mb-4">
            <TrendingUp className="text-blue-600 w-6 h-6" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Analyse détaillée</h3>
          <p className="text-gray-600">
            Suivez l'évolution et la croissance des entreprises avec des données actualisées.
          </p>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-white rounded-2xl p-8 shadow-lg">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          L'Île-de-France en chiffres
        </h2>
        <div className="grid md:grid-cols-4 gap-8 text-center">
          <div>
            <p className="text-3xl font-bold text-blue-600">1.2M+</p>
            <p className="text-gray-600">Entreprises</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-blue-600">8</p>
            <p className="text-gray-600">Départements</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-blue-600">12.2M</p>
            <p className="text-gray-600">Habitants</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-blue-600">31%</p>
            <p className="text-gray-600">du PIB national</p>
          </div>
        </div>
      </div>
    </div>
  );
}