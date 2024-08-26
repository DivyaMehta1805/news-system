import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import Header from './Header';
import { useNavigate } from 'react-router-dom';

function App() {
  const [articles, setArticles] = useState([]);
  const [anonymousId, setAnonymousId] = useState('');
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleArticleClick = (article) => {
    recordArticleInteraction(article.title_1);
    navigate('/article');
  };
  
  useEffect(() => {
    const id = getOrCreateAnonymousId();
    setAnonymousId(id);
  }, []);

  useEffect(() => {
    if (anonymousId) {
      fetchRecommendations();
    }
  }, [anonymousId]);

  const getOrCreateAnonymousId = () => {
    let id = localStorage.getItem('anonymousId');
    if (!id) {
      id = generateAnonymousId();
      localStorage.setItem('anonymousId', id);
    }
    return id;
  };

  const generateAnonymousId = () => {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  };

  const fetchRecommendations = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/api/get-recommendations?userId=${anonymousId}`);
      if (Array.isArray(response.data) && response.data.length > 0) {
        setArticles(response.data);
        setError(null);
      } else if (Array.isArray(response.data) && response.data.length === 0) {
        setError('No recommendations available');
        setArticles([]);
      } else {
        console.error('Received unexpected response:', response.data);
        setError('Received unexpected data format from server');
        setArticles([]);
      }
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      setError('Failed to fetch recommendations');
      setArticles([]);
    }
  };

  const recordArticleInteraction = async (articleTitle) => {
    try {
      console.log(`Recording interaction for article: ${articleTitle}`);
      const response = await axios.post('http://localhost:5000/api/record-interaction', {
        userId: anonymousId,
        articleTitle: articleTitle,
        interactionType: 'view'
      });
      console.log('Interaction recorded successfully');
      console.log('Response:', response.data);
      if (response.data.newRecommendations) {
        setArticles(response.data.newRecommendations);
      }
    } catch (error) {
      console.error('Error recording interaction:', error.response ? error.response.data : error.message);
    }
  };

  return (
    <div className="App">
      <Header/>
      <main className="main-content">
        <div className="container">
          <h1 className="page-title">News Recommendations</h1>
          <div className="anonymous-id">
            <p>Your Anonymous ID: {anonymousId}</p>
          </div>
          {error && <p className="error">{error}</p>}
          <div className="article-grid">
            {Array.isArray(articles) && articles.map((article, index) => (
              <div key={index} className="article-card" onClick={() => handleArticleClick(article)}>
                <h2 className="article-title">{article.title_1}</h2>
                <p className="article-excerpt">
                  {article.content_1 ? article.content_1.substring(0, 200) + '...' : 'No content available'}
                </p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;