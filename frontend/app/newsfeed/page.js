'use client'

import { useEffect, useState } from 'react';
import axios from 'axios';
import styles from '../../styles/newsfeed.module.scss';

const NewsFeed = () => {
  const [newsFeed, setNewsFeed] = useState([]);
  const [showPersonalized, setShowPersonalized] = useState(true); // Default to showing personalized feed

  useEffect(() => {
    const fetchNewsFeed = async () => {
      try {
        const response = await axios.get('https://halal-stonks-backend.vercel.app/api/get_newsfeed'); // Fetch data from your FastAPI endpoint
        setNewsFeed(response.data.data); // Assuming your backend returns { message: ..., data: ... }
      } catch (error) {
        console.error('Error fetching news feed:', error);
        setNewsFeed([]); // Clear feed on error
      }
    };

    fetchNewsFeed();
  }, []);

  const handleToggle = () => {
    setShowPersonalized(!showPersonalized); // Toggle between personalized and explore feeds
  };

  return (
    <div className={styles.container}>
      <div className={styles.toggleContainer}>
        <button
          className={`${styles.toggleButton} ${showPersonalized ? styles.active : ''}`}
          onClick={handleToggle}
        >
          Personalized
        </button>
        <button
          className={`${styles.toggleButton} ${!showPersonalized ? styles.active : ''}`}
          onClick={handleToggle}
        >
          Explore
        </button>
      </div>
      <div className={styles.tab}>
        <ul className={styles.articleList}>
          {newsFeed.map((article, index) => (
            <li key={index} className={styles.article}>
              <div className={styles.articleContent}>
                <div className={styles.articleImage}>
                  {article.image && <img src={article.image} alt={article.title} />}
                </div>
                <div className={styles.articleDetails}>
                  <h3 className={styles.heading3}>{article.title}</h3>
                  <p className={styles.paragraph}>{article.description}</p>
                  <a href={article.url} target="_blank" rel="noopener noreferrer" className={styles.link}>Read more</a>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default NewsFeed;
