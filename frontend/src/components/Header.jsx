import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Menu, X, LogOut } from 'lucide-react';
import { Button } from '../components/ui/button';

const Header = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  return (
    <header className="nav-header">
      <div className="flex items-center">
        <Link to="/" className="flex items-center space-x-2">
          <img 
            src="https://customer-assets.emergentagent.com/job_easy-loan-access/artifacts/nsaqwx8u_1000315618-removebg-preview.png" 
            alt="Cashflow MFB" 
            className="h-10 w-auto"
          />
        </Link>
      </div>

      {/* Desktop Navigation */}
      <nav className="hidden md:flex items-center space-x-1">
        <a href="#about" className="nav-link body-medium">
          About
        </a>
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
      <button
        className="md:hidden"
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
      >
        {mobileMenuOpen ? <X /> : <Menu />}
      </button>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="absolute top-14 left-0 right-0 bg-white border border-gray-200 shadow-lg md:hidden">
          <nav className="flex flex-col p-4 space-y-2">
            <a href="#about" className="nav-link">
              About
            </a>
            <a href="#why-choose-us" className="nav-link">
              Why Us
            </a>
            <a href="#repayment" className="nav-link">
              Repayment
            </a>
            <a href="#contact" className="nav-link">
              Contact
            </a>
            {isAuthenticated ? (
              <>
                <Link to={user?.role === 'admin' ? '/admin' : '/dashboard'}>
                  <button className="btn-secondary w-full">Dashboard</button>
                </Link>
                <button
                  onClick={logout}
                  className="btn-secondary w-full"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login">
                  <button className="btn-secondary w-full">Login</button>
                </Link>
                <Link to="/apply">
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
