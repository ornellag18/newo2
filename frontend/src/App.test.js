import { render, screen } from '@testing-library/react';
import App from './App';

test('renders Newo logo', () => {
  render(<App />);
  const logoElement = screen.getByAltText(/Newo Logo/i);
  expect(logoElement).toBeInTheDocument();
});

