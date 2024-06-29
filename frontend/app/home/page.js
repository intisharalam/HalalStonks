"use client"

// Import useState and useRouter from React and Next.js
import React, { useState } from 'react';
import Image from "next/image";
import Logo from "../../public/Logo-black-2.svg";
import styles from "../../styles/home.module.scss";
import { useRouter } from 'next/navigation';

export default function HomePage() {
    const [symbol, setSymbol] = useState('');
    const router = useRouter();

    const handleRedirect = () => {
      router.push(`/dashboard`);
    };

    return (
        <div className={styles.container_home}>
            <div className={styles.container_search}>
                <Image
                    className={styles.logoImg}
                    src={Logo}
                    width={224}
                    height={224}
                    alt="logo"
                />
                <button onClick={handleRedirect} className={styles.redirectButton}>
                    Go to Dashboard
                </button>
            </div>
            <div className={styles.container_intro}>
                <h1 className={styles.intro_greet}>Welcome!</h1>
                <h2 className={styles.intro_subheading}>Here is how the site works👇</h2>
                <p className={styles.intro_text}>
                    Enter the ticker symbol or name of the company you are looking into.
                    Once you click on the stock you wish to check, you will be redirected to the dashboard for more details.
                    You may also be interested in checking the newsfeed for popular general stocks or Halal stocks.<br /><br />
                    <strong>Note:</strong> This is a DIY project created by a student engineer, so there may be some errors. It is not developed by a financial expert.
                </p>
            </div>
        </div>
    );
}
