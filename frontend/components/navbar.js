"use client"

import styles from "../styles/navbar.module.scss";
import React from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { useState, useEffect } from "react";

import { Inter } from "next/font/google";

const links = [
    ["Home", "/home"],
    ["Dashboard", "/dashboard"],
    ["Newsfeed", "/newsfeed"],
];
const inter = Inter({ subsets: ["latin"] });


function NavListItem({ arrItems = [] }) {
    const pathname = usePathname();

    return (
        arrItems.map((linkList) => {
            console.log("pathname:", pathname);
            console.log("linkList[1]:", linkList[1]);

            const isActive = pathname.startsWith(linkList[1]);
            
            return (
                <li key={linkList[0]} className={isActive ? styles.active : ""}>
                    <Link href={linkList[1]}>
                        {linkList[0]}
                    </Link>
                </li>
            );
        })
    );
}

export default function Navbar() {
    const [navActive, setNavActive] = useState(false);

    // Function to handle scrolling behavior
    const handleScroll = () => {
        const body = document.body;
        const html = document.documentElement;
        if (navActive) {
            window.scrollTo(0, 0);
            body.style.overflow = "hidden";
            html.style.overflow = "hidden";
        } else {
            body.style.overflow = "auto";
            html.style.overflow = "auto";
        }
    };

    // Add an event listener to handle scrolling when `navActive` changes
    useEffect(() => {
        handleScroll();
    }, [navActive]);

    return (
        <nav className={styles.nav}>
            <div className={styles.navTop}>
                <Link href="/home" className={styles.siteName}>
                    <h1>Halal Stonks</h1>
                </Link>

                <div onClick={() => setNavActive(!navActive)} className={`${styles.nav_menu_bar} ${navActive ? styles.nav_menu_bar_active : ""}`}>
                    <div></div>
                    <div></div>
                    <div></div>
                </div>
            </div>

            <ul onClick={() => setNavActive(false)} className={`${styles.nav_menu_list} ${navActive ? styles.nav_menu_list_active : ""}`}>
                <NavListItem arrItems={links} />
            </ul>
        </nav>
    );
}
