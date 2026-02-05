# Attendance System - Render Deployment Guide

## Step-by-Step Deployment Instructions

### 1. **Prepare Your GitHub Repository**

First, you need to push your project to GitHub:

```bash
cd "C:\Users\SCATTER ONLY\attendance system\attendance_project"
git init
git add .
git commit -m "Initial commit - Attendance System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/attendance-system.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

### 2. **Create Render Account**

- Go to https://render.com
- Sign up using your GitHub account (recommended)
- Verify your email

### 3. **Create PostgreSQL Database on Render**

1. Click "New +" → Select "PostgreSQL"
2. Fill in:
   - **Name**: `attendance-db`
   - **Database**: `attendance`
   - **User**: `attendance_user`
   - **Region**: Choose closest to you
   - **Plan**: Free (default)
3. Click "Create Database"
4. Wait for it to be created (~2 minutes)
5. Copy the connection string (you'll need it later)

### 4. **Create Web Service on Render**

1. Click "New +" → Select "Web Service"
2. Choose "Deploy from a Git repository"
3. Select your `attendance-system` repository
4. Fill in:
   - **Name**: `attendance-system` (or any name)
   - **Environment**: `Python 3`
   - **Build Command**: `./build.sh` (or `bash build.sh`)
   - **Start Command**: `gunicorn attendance_project.wsgi:application`
   - **Plan**: Free (default)

### 5. **Configure Environment Variables**

In the Render dashboard, go to your Web Service and click on "Environment":

Add these environment variables:

```
DEBUG=False
SECRET_KEY=your-very-long-random-secret-key-here
ALLOWED_HOSTS=your-service-name.onrender.com
DATABASE_URL=postgres://USERNAME:PASSWORD@HOST/DATABASE
DB_ENGINE=postgresql
```

**To get DATABASE_URL:**
- Go to your PostgreSQL database in Render
- Copy the "External Database URL" from the Info tab
- It looks like: `postgres://user:password@host:5432/database`

**To generate SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 6. **Deploy**

1. After setting environment variables, click "Deploy"
2. Wait for the build to complete (5-10 minutes for free tier)
3. Check the logs for any errors

### 7. **Create Superuser (Admin Account)**

Once deployment is complete:

1. Go to your Render dashboard
2. Find your Web Service
3. Click on "Shell" tab
4. Run this command:

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### 8. **Access Your Application**

- Open your browser and go to: `https://your-service-name.onrender.com`
- Admin panel: `https://your-service-name.onrender.com/admin/`

### 9. **Add Initial Data (Optional)**

To add the sample students back:

1. Go to Admin panel (`/admin/`)
2. Login with your superuser account
3. Add students manually or via CSV upload

Or create a management command to load sample data.

---

## Important Notes

### Free Tier Limitations:
- ⚠️ **Spins down after 15 minutes of inactivity** - first request will be slow
- Limited to 100MB storage
- Shared database resources
- Database and service auto-sleep if inactive

### To Prevent Spinning Down:
- Use a monitoring service (Uptimerobot.com - free tier available)
- Set it to ping your app every 14 minutes

### Database Backups:
- Free tier doesn't include automated backups
- Manually export data before major changes

### Troubleshooting:

**502 Bad Gateway Error:**
- Check Render logs for errors
- Ensure all environment variables are set correctly
- Run migrations: Use Render Shell to execute `python manage.py migrate`

**Database Connection Error:**
- Verify DATABASE_URL is correct
- Check that DB_ENGINE is set to 'postgresql'

**Static Files Not Loading:**
- Run `python manage.py collectstatic --noinput` in shell
- WhiteNoise should handle this automatically

---

## Files Created for Deployment:

- ✅ `Procfile` - Tells Render how to run the app
- ✅ `runtime.txt` - Specifies Python version
- ✅ `build.sh` - Build script for deployment
- ✅ `.gitignore` - Prevents pushing sensitive files
- ✅ Updated `settings.py` - Production configuration
- ✅ Updated `requirements.txt` - All necessary packages

---

## Next Steps:

1. Push to GitHub
2. Sign up on Render
3. Create PostgreSQL database
4. Create Web Service
5. Add environment variables
6. Deploy!

Need help? Check Render's documentation: https://docs.render.com
