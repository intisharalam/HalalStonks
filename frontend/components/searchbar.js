import React, { useRef, useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import styles from '../styles/searchbar.module.scss';

function SearchBar({ onSelect }) {
    const [isOpen, setIsOpen] = useState(false);
    const [results, setResults] = useState([]);
    const inputRef = useRef(null);
    const dropdownRef = useRef(null);

    useEffect(() => {
        function handleClickOutside(event) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false); // Close dropdown when clicked outside
            }
        }

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    const handleInputFocus = () => {
        setIsOpen(true); // Open dropdown when input is focused
    };

    const handleSearch = async (query) => {
        if (query.trim() === '') {
            setResults([]);
            return;
        }
    
        try {
            const apiUrl = `https://halal-stonks-backend.vercel.app/api/search_symbols`;
            const response = await axios.post(apiUrl, { query });
    
            if (response.data.results) {
                const items = response.data.results.map(item => ({
                    name: item.name,
                    symbol: item.symbol
                }));
    
                setResults(items);
                setIsOpen(true); // Open dropdown with results
            } else {
                console.warn('No matches found or unexpected response structure:', response.data);
                setResults([]);
            }
        } catch (error) {
            console.error('Error fetching stock symbols:', error);
            setResults([]);
        }
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter') {
            handleSearch(event.target.value);
        }
    };

    const handleSelect = (symbol) => {
        setIsOpen(false); // Close dropdown when an item is selected
        onSelect(symbol); // Trigger onSelect function passed from props
    };

    return (
        <div className={styles.searchBar}>
            <input
                type="text"
                placeholder="🔍 Search company..."
                className={styles.input}
                ref={inputRef}
                onKeyPress={handleKeyPress}
                onFocus={handleInputFocus}
            />
            {isOpen && results.length > 0 && (
                <ul ref={dropdownRef} className={styles.dropdown}>
                    {results.map((result, index) => (
                        <li
                            key={index}
                            className={styles.dropdownItem}
                            onClick={() => handleSelect(result.symbol)}
                        >
                            {result.name}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}

SearchBar.propTypes = {
    onSelect: PropTypes.func.isRequired,
};

export default SearchBar;
