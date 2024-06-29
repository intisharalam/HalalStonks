import React from 'react';
import PropTypes from 'prop-types';
import styles from '../styles/criteriatable.module.scss'; // Assuming you have a CSS module for styles

const CriteriaTable = ({ criteriaData, title }) => {
  return (
    <div className={styles.table_container}>
      <div className={styles.table_title}>
        <h2>{title}:</h2>
      </div>
      <table className={styles.table}>
        <thead>
          <tr className={styles.table_header}>
            <th>Criteria</th>
            <th>Limit</th>
            <th>Result</th>
          </tr>
        </thead>
        <tbody>
          {criteriaData.map((row, index) => (
            <tr key={index} className={styles.table_row}>
              <td>{row.criteria || row.title}</td>
              <td>{row.limit}</td>
              <td>{row.result}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

CriteriaTable.propTypes = {
  criteriaData: PropTypes.array.isRequired,
  title: PropTypes.string.isRequired,
  score: PropTypes.string.isRequired,
};

export default CriteriaTable;
