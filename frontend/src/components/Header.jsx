import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Menu, X, LogOut, Moon, Sun } from 'lucide-react';
import { Button } from '../components/ui/button';

const LOGO_URL = "https://customer-assets.emergentagent.com/job_microfin-portal/artifacts/yv8s58dq_1000315618-removebg-preview.png";

const Header = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const { isDarkMode, toggleTheme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  return (
    <header className={`nav-header ${isDarkMode ? 'dark-header' : ''}`}>
      <div className="flex items-center">
        <Link to="/" className="flex items-center space-x-2">
          <img 
            src={LOGO_URL}
            alt="Cashflow MFB" 
            className="h-10 w-auto"
          />
        </Link>
      </div>

      {/* Desktop Navigation */}
      <nav className="hidden md:flex items-center space-x-1">
        <Link to="/about" className="nav-link body-medium">
          About
        </Link>
        <a href="#why-choose-us" className="nav-link body-medium">
          Why Us
        </a>
        <a href="#repayment" className="nav-link body-medium">
          Repayment
        </a>
        <a href="#contact" className="nav-link body-medium">
          Contact
        </a>
      </nav>

      <div className="hidden md:flex items-center space-x-2">
        {/* Dark Mode Toggle */}
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleTheme}
          className="rounded-full"
          title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
          {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </Button>
        
        {isAuthenticated ? (
          <>
            <Link to={user?.role === 'admin' ? '/admin' : '/dashboard'}>
              <Button variant="ghost" className="rounded-full">
                Dashboard
              </Button>
            </Link>
            <Button
              variant="ghost"
              onClick={logout}
              className="rounded-full"
            >
              <LogOut className="w-4 h-4" />
            </Button>
          </>
        ) : (
          <>
            <Link to="/login">
              <button className="btn-secondary">Login</button>
            </Link>
            <Link to="/apply">
              <button className="btn-primary">Apply Now</button>
            </Link>
          </>
        )}
      </div>

      {/* Mobile Menu Button */}
      <div className="flex items-center gap-2 md:hidden">
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleTheme}
          className="rounded-full"
        >
          {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </Button>
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          {mobileMenuOpen ? <X /> : <Menu />}
        </button>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className={`absolute top-14 left-0 right-0 ${isDarkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-gray-200'} border shadow-lg md:hidden z-50`}>
          <nav className="flex flex-col p-4 space-y-2">
            <Link to="/about" className="nav-link" onClick={() => setMobileMenuOpen(false)}>
              About
            </Link>
            <a href="#why-choose-us" className="nav-link" onClick={() => setMobileMenuOpen(false)}>
              Why Us
            </a>
            <a href="#repayment" className="nav-link" onClick={() => setMobileMenuOpen(false)}>
              Repayment
            </a>
            <a href="#contact" className="nav-link" onClick={() => setMobileMenuOpen(false)}>
              Contact
            </a>
            {isAuthenticated ? (
              <>
                <Link to={user?.role === 'admin' ? '/admin' : '/dashboard'} onClick={() => setMobileMenuOpen(false)}>
                  <button className="btn-secondary w-full">Dashboard</button>
                </Link>
                <button
                  onClick={() => { logout(); setMobileMenuOpen(false); }}
                  className="btn-secondary w-full"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" onClick={() => setMobileMenuOpen(false)}>
                  <button className="btn-secondary w-full">Login</button>
                </Link>
                <Link to="/apply" onClick={() => setMobileMenuOpen(false)}>
                  <button className="btn-primary w-full">Apply Now</button>
                </Link>
              </>
            )}
          </nav>
        </div>
      )}
    </header>
  );
};

export default Header;
