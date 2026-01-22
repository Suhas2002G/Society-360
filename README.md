# Society 360 - Society Management System

## Project Title
"Hello everyone, my project title is Society 360, which is a Society Management System designed to make residential community management efficient, streamlined, and hassle-free for both owners and administrators."

## Objectives
The main objectives of the Society 360 project are:
- To provide a centralized platform for owners to manage notices, pay maintenance, and book amenities.
- To create a smooth and user-friendly interface for administrators to manage notices, payments, and complaints.
- To offer secure and convenient features like Razorpay payment integration and email notifications for better communication.

## Problem Statements
Residential societies often face challenges like:
- Difficulty in communicating notices and updates to the residents.
- Issues with timely payment of maintenance bills.
- Complicated manual processes for amenity bookings and complaints.
- Lack of transparency in society management.

Society 360 aims to solve these problems by providing a platform that is easy to use, reliable, and efficient.

## Features and Functionality
### For Owners:
- **User Authentication** – Owners can register and log in to access personalized features.
- **Notice Board** – Owners can view the latest notices posted by the admin.
- **Payment of Maintenance** – Secure online payment integration through Razorpay for monthly maintenance.
- **Amenity Booking** – Owners can book amenities like the turf, seminar-hall, etc.
- **Raise Complaints** – Owners can raise complaints regarding any issues in the society.
- **Email Integration** – Owners will receive email notifications for activities like payment confirmation, amenity booking updates, etc.

### For Admin:
- **Notice Management** – Admins can post and manage notices.
- **Maintenance Dashboard** – Admins can view and manage maintenance payments.
- **Amenity Management** – Admins can add and update details for various amenities.
- **Owner Management** – Admin can view and manage the list of owners.
- **Complaint Dashboard** – Admin can view complaints raised by owners and track their resolution.

## Development Workflow
### Frontend Development
The frontend was developed using HTML, CSS, JavaScript, and Bootstrap to ensure the application is visually appealing and responsive. We focused on creating an intuitive user interface where both owners and admins can navigate seamlessly across the platform.

### Backend Development
The backend is powered by Python and Django. Django was chosen for its built-in features like authentication, admin dashboard, and scalability. It handles user authentication, CRUD operations for notices, amenities, and complaints, as well as payment processing.

### Database Design
We are using MySQL for the database. The database schema includes tables for:
- **Auth-User** (owners and admin)
- **Notices**
- **Payments**
- **Amenities**
- **Complaints**

This structure ensures data integrity, ease of access, and efficient management of the system.

### Class Diagram
![Class Diagram](documentation/class_diagram/class_diagram_svg.svg)


## Project Scope
The scope of Society 360 includes:
- Managing day-to-day operations of a residential society through a centralized platform.
- Enabling both owners and admins to perform their respective tasks efficiently.
- Supporting future updates and features like SMS integration or multi-language support.

## End Users
The end users of the system are:
- Owners of residential societies who need to interact with notices, payments, and amenities.
- Admin(s) responsible for managing the society’s operations, including maintaining the database, handling complaints, and posting notices.

## Limitations
Some of the limitations of this project include:
- The system currently supports only online payments through Razorpay and may need integration with other payment systems in the future.
- It is currently designed for a single society and will require further customization to be used by multiple societies.
- We have not yet implemented a mobile app version, but this could be part of future development.

## Conclusion
In conclusion, Society 360 is an innovative and effective solution for society management, bringing all essential features together into one platform. By automating tasks like payments, complaints, and amenity bookings, we aim to reduce manual effort and improve the overall experience for both owners and administrators. The project is scalable, secure, and efficient, with room for future enhancements based on user feedback.
