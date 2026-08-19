import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Loading, ErrorMessage } from './src/components/common/Common';
import React from 'react';

describe('Common Components', () => {
  it('renders loading spinner', () => {
    const { container } = render(<Loading />);
    expect(container.querySelector('.animate-spin')).not.toBeNull();
  });

  it('renders error message correctly', () => {
    render(<ErrorMessage message="API Failure 500" />);
    expect(screen.getByText('API Failure 500')).toBeDefined();
    expect(screen.getByText('Error:')).toBeDefined();
  });
});
