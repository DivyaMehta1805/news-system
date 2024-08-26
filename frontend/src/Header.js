import React from 'react';
import './Header.css';

function Header() {
  const links = [
    { name: 'Home', url: '/' },
    { name: 'Categories', url: '/categories' },
    { name: 'Trending', url: '/trending' },
    { name: 'Subscribe', url: '/subscribe' }
  ];

  return (
    <header className="header">
      <div className="header-content">
        <div className="logo-container">
          <h1 className="logo">
            <span className="logo-text">News</span>
            <span className="logo-highlight">Hub</span>
          </h1>
        </div>
        <nav className="nav">
          {links.map((link, index) => (
            <a key={index} href={link.url} className="nav-link">
              {link.name}
            </a>
          ))}
        </nav>
      </div>
    </header>
  );
}

export default Header;