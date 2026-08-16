// src/pages/Blog.jsx
import './LegalPages.css';

export const Blog = () => {
  const posts = [
    {
      id: 1,
      title: 'How ArtisanHub is Transforming Field Service Management',
      excerpt: 'Discover how our platform is helping businesses reduce response times by 60%...',
      date: 'July 10, 2026',
      category: 'Industry Insights',
    },
    {
      id: 2,
      title: '5 Tips for Onboarding Artisans Effectively',
      excerpt: 'Learn the best practices for bringing new artisans onto your platform...',
      date: 'July 5, 2026',
      category: 'Best Practices',
    },
    {
      id: 3,
      title: 'The Future of Work: AI and Workforce Management',
      excerpt: 'How artificial intelligence is shaping the future of dispatching and field service...',
      date: 'June 28, 2026',
      category: 'Technology',
    },
    {
      id: 4,
      title: 'Building Trust: The Importance of Artisan Verification',
      excerpt: 'Why KYC verification is crucial for platform safety and customer confidence...',
      date: 'June 20, 2026',
      category: 'Safety & Trust',
    },
  ];

  return (
    <div className="legal-page">
      <div className="container">
        <h1>Blog</h1>
        <div className="legal-content">
          <p>Insights, updates, and stories from the ArtisanHub team.</p>
          <div className="blog-grid">
            {posts.map((post) => (
              <div key={post.id} className="blog-card">
                <span className="blog-category">{post.category}</span>
                <h3>{post.title}</h3>
                <p>{post.excerpt}</p>
                <span className="blog-date">{post.date}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};