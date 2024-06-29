import React from 'react';
import styles from '../styles/card.module.scss'

export default function Card ({ topText, middleText, bottomText }) {
  return (
    <div className={styles.container}>
      <div>
        <p className={styles.topText}>{topText}</p>
      </div>
      <div>
        <p className={styles.middleText}>{middleText}</p>
      </div>
      <div>
        <p className={styles.bottomText}>{bottomText}</p>
      </div>
    </div>
  );
};