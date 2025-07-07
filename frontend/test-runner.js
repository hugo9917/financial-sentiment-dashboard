// Simple test runner for frontend components
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🧪 Running Frontend Tests...\n');

// Test 1: Check if main components exist
const components = [
  'src/pages/Dashboard.jsx',
  'src/pages/Correlation.jsx',
  'src/pages/News.jsx',
  'src/components/Navbar.jsx',
  'src/App.jsx'
];

console.log('📁 Checking component files...');
components.forEach(component => {
  if (fs.existsSync(component)) {
    console.log(`✅ ${component} exists`);
  } else {
    console.log(`❌ ${component} missing`);
  }
});

// Test 2: Check if package.json has required dependencies
console.log('\n📦 Checking package.json...');
const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
const requiredDeps = ['react', 'react-dom', 'react-router-dom', 'chart.js', 'react-chartjs-2'];

requiredDeps.forEach(dep => {
  if (packageJson.dependencies[dep] || packageJson.devDependencies[dep]) {
    console.log(`✅ ${dep} is installed`);
  } else {
    console.log(`❌ ${dep} is missing`);
  }
});

// Test 3: Check if vite config exists
console.log('\n⚙️ Checking Vite configuration...');
if (fs.existsSync('vite.config.js')) {
  console.log('✅ vite.config.js exists');
} else {
  console.log('❌ vite.config.js missing');
}

// Test 4: Check if test files exist
console.log('\n🧪 Checking test files...');
const testFiles = [
  'src/test/Dashboard.test.jsx',
  'src/test/News.test.jsx',
  'src/test/Login.test.jsx',
  'src/test/setup.js'
];

testFiles.forEach(testFile => {
  if (fs.existsSync(testFile)) {
    console.log(`✅ ${testFile} exists`);
  } else {
    console.log(`❌ ${testFile} missing`);
  }
});

console.log('\n🎉 Frontend test checks completed!');
console.log('Note: For full component testing, install vitest and run: npm test'); 