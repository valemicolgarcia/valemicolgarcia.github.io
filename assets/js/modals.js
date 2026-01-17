// Certificate image paths
const certificateImages = {
  'data-science-i-2024': '/files/certificates/data-science-i-2024.png',
  'data-science-ii-2024': '/files/certificates/data-science-ii-2024.png',
  'data-science-iii-2024': '/files/certificates/data-science-iii-2024.png',
  'machine-learning-python-2024': '/files/certificates/ml-freecodecamp.png',
  'cloud-computing-2024': '/files/certificates/aws-2024.png',
  'backend-i-2025': '/files/certificates/backend-i.png',
  'backend-ii-2025': '/files/certificates/backend-ii-2025.png',
  'sql-2025': '/files/certificates/sql.png'
};

// Course topics data
const courseTopics = {
  'data-science-i-2024': [
    'Information in Industry 4.0',
    'Data Scientist Tech Stack',
    'Basic Python',
    'Pandas',
    'Numpy',
    'Data Manipulation',
    'Matplotlib',
    'Seaborn',
    'Advanced Visualization',
    'Descriptive Statistics',
    'Statistical Preprocessing',
    'Supervised/Unsupervised Learning',
    'AI Introduction',
    'Model Validation'
  ],
  'data-science-ii-2024': [
    'Database Fundamentals',
    'Data Acquisition',
    'Advanced SQL',
    'Data Wrangling',
    'Exploratory Data Analysis (EDA)',
    'Storytelling',
    'Animated Visualizations',
    'Univariate/Bivariate/Multivariate Analysis',
    'Classification & Regression Algorithms',
    'Model Improvement',
    'Ensemble Methods',
    'Evaluation Metrics'
  ],
  'data-science-iii-2024': [
    'Foundations of NLP',
    'Introduction to Deep Learning',
    'Perceptron & MLP',
    'Convolutional Neural Networks (CNN)',
    'Recurrent Neural Networks (RNN)'
  ],
  'machine-learning-python-2024': [
    'ML Fundamentals',
    'Core Learning Algorithms (Regression, Classification, Clustering, Hidden Markov Models)',
    'Neural Networks (Activation Functions, Optimizers)',
    'CNNs (Pretrained Models)',
    'NLP with RNNs (Sentiment Analysis, Play Generator)',
    'Reinforcement Learning with Q-Learning'
  ],
  'cloud-computing-2024': [
    'Cloud Computing Fundamentals',
    'IAM',
    'EC2',
    'VPC',
    'S3',
    'RDS',
    'DynamoDB',
    'CloudWatch & CloudFormation',
    'Athena',
    'IoT Core',
    'Lambda',
    'Cloud Project Management'
  ],
  'backend-i-2025': [
    'Relational Databases',
    'SQL Sentences',
    'DDL/DML/DCL/TCL',
    'Stored Procedures',
    'Triggers',
    'Transactions & Backup',
    'Data Warehouse',
    'Business Intelligence'
  ],
  'backend-ii-2025': [
    'Backend Principles',
    'JavaScript/ECMAScript',
    'Asynchronous Programming',
    'Node.js',
    'File Management',
    'Express',
    'WebSockets',
    'MongoDB (Indexing & Populations)',
    'Authentication & Authorization (Passport, JWT, OAuth)',
    'Layered Architecture',
    'Singleton Pattern'
  ],
  'sql-2025': [
    'SQL Fundamentals',
    'Database Design',
    'Query Optimization'
  ]
};

// Experience details
const experienceDetails = {
  'ayudante-programacion-2': [
    'Recursion',
    'Composite non-linear data structures (Trees)',
    'Memory and peripherals',
    'Functional computer organization',
    'Introduction to Object-Oriented Programming (OOP)',
    'Introduction to Concurrency',
    'Programming Paradigms'
  ]
};

// Initialize modals when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  // Handle course clicks
  document.querySelectorAll('.content-link[href^="/certificates/"]').forEach(link => {
    link.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      const courseId = href.replace('/certificates/', '').replace('.html', '');
      
      if (courseTopics[courseId]) {
        e.preventDefault();
        showCourseModal(courseId, this);
      }
    });
  });

  // Handle clickable experience items
  document.querySelectorAll('.clickable-experience').forEach(item => {
    item.style.cursor = 'pointer';
    item.addEventListener('click', function(e) {
      const experienceId = this.getAttribute('data-experience');
      if (experienceId) {
        showExperienceModal(experienceId, this);
      }
    });
  });
});

function showCourseModal(courseId, triggerElement) {
  const topics = courseTopics[courseId];
  if (!topics) return;

  const courseTitle = triggerElement.querySelector('h3')?.textContent || 'Course';
  
  // Create modal HTML
  const modalHTML = `
    <div class="course-modal-overlay" id="courseModal">
      <div class="course-modal">
        <div class="course-modal-header">
          <h2>${courseTitle}</h2>
          <button class="course-modal-close" onclick="closeCourseModal()">&times;</button>
        </div>
        <div class="course-modal-body">
          <h3>Topics Learned</h3>
          <ul class="course-topics-list">
            ${topics.map(topic => `<li>${topic}</li>`).join('')}
          </ul>
          ${courseId === 'cloud-computing-2024' ? `
            <div class="aws-project-section">
              <h3>Project: Cloud Architecture Design</h3>
              <div class="aws-architecture-image">
                <img src="/files/cursos/arquiAWS.png" alt="AWS Architecture" />
              </div>
              <a href="/files/cursos/awsProyecto.pdf" download class="aws-download-btn">
                <i class="fas fa-download"></i> Download Project PDF
              </a>
            </div>
          ` : ''}
          ${certificateImages[courseId] ? `
            <div class="certificate-image-section">
              <h3>Certificate</h3>
              <div class="certificate-image-modal">
                <img src="${certificateImages[courseId]}" alt="${courseTitle} Certificate" />
              </div>
            </div>
          ` : ''}
        </div>
        <div class="course-modal-footer">
          <a href="/certificates/${courseId}" class="course-modal-cert-link">View Certificate Page</a>
        </div>
      </div>
    </div>
  `;

  // Add modal to body
  document.body.insertAdjacentHTML('beforeend', modalHTML);
  document.body.style.overflow = 'hidden';

  // Close on overlay click
  document.getElementById('courseModal').addEventListener('click', function(e) {
    if (e.target.id === 'courseModal') {
      closeCourseModal();
    }
  });
}

function showExperienceModal(experienceId, triggerElement) {
  const details = experienceDetails[experienceId];
  if (!details) return;

  const experienceTitle = triggerElement.querySelector('h3')?.textContent || 'Experience';
  
  // Create modal HTML
  const modalHTML = `
    <div class="course-modal-overlay" id="experienceModal">
      <div class="course-modal">
        <div class="course-modal-header">
          <h2>${experienceTitle}</h2>
          <button class="course-modal-close" onclick="closeExperienceModal()">&times;</button>
        </div>
        <div class="course-modal-body">
          <h3>Course Contents</h3>
          <ul class="course-topics-list">
            ${details.map(item => `<li>${item}</li>`).join('')}
          </ul>
        </div>
      </div>
    </div>
  `;

  // Add modal to body
  document.body.insertAdjacentHTML('beforeend', modalHTML);
  document.body.style.overflow = 'hidden';

  // Close on overlay click
  document.getElementById('experienceModal').addEventListener('click', function(e) {
    if (e.target.id === 'experienceModal') {
      closeExperienceModal();
    }
  });
}

function closeCourseModal() {
  const modal = document.getElementById('courseModal');
  if (modal) {
    modal.remove();
    document.body.style.overflow = '';
  }
}

function closeExperienceModal() {
  const modal = document.getElementById('experienceModal');
  if (modal) {
    modal.remove();
    document.body.style.overflow = '';
  }
}

// Close on Escape key
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    closeCourseModal();
    closeExperienceModal();
  }
});
