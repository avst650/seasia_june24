-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 26, 2022 at 06:51 AM
-- Server version: 10.4.24-MariaDB
-- PHP Version: 8.1.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `weeknd`
--

-- --------------------------------------------------------

--
-- Table structure for table `contacts`
--

CREATE TABLE `contacts` (
  `serial_number` int(50) NOT NULL,
  `name` text NOT NULL,
  `email` varchar(50) NOT NULL,
  `phone_number` varchar(50) NOT NULL,
  `message` varchar(50) NOT NULL,
  `date` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `contacts`
--

INSERT INTO `contacts` (`serial_number`, `name`, `email`, `phone_number`, `message`, `date`) VALUES
(1, 'first post', 'firstpost@gmail.com', '1234567890', 'boo', '2022-07-20 12:09:56'),
(2, 'hiee', 'hiee@gmail.com', '1212121212', 'hiee coo', '2022-07-20 12:55:01'),
(3, 'real gone', 'cars@gmail.com', '2006200620', 'slow down you gonna crash, baby you keep sayin its', '2022-07-20 14:28:40'),
(4, 'after hours', 'ah2@gmail.com', '', '', '2022-07-20 17:37:10');

-- --------------------------------------------------------

--
-- Table structure for table `posts`
--

CREATE TABLE `posts` (
  `serial_number` int(11) NOT NULL,
  `title` varchar(50) NOT NULL,
  `tagline` text NOT NULL,
  `slug` varchar(25) NOT NULL,
  `content` varchar(200) NOT NULL,
  `img_file` varchar(100) NOT NULL,
  `date` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `posts`
--

INSERT INTO `posts` (`serial_number`, `title`, `tagline`, `slug`, `content`, `img_file`, `date`) VALUES
(1, 'Is there someone else', 'every angel is terrifying', 'is', 'lyrics: i know that you\'re hiding something from me thats  been close to your heartand i felt it creepin up everyday baby right from the start and i know that love you give when we\'re fighting', 'post-bg.png', '2022-07-25 12:19:07'),
(2, 'out of time', 'don\'t you dare touch that dial cuz the song says you\'re out of time', 'out', 'say i love you girl but i\'m out of time, say i\'m there for you but i\'m out of time, say i care for you but i\'m out of time\r\n\r\nsaid i\'m too late to make you mine, out of time.', 'about-bg.png', '2022-07-21 15:14:03'),
(3, 'gasoline', 'you have been in the dark for way too long', 'gasoline', 'its 5 am and i\'m nihilist, i know there\'s nothing after this, obsessing for the aftermath, apocalypse and hopelessness', 'gasoline.png', '2022-07-21 16:17:00'),
(5, 'Save your tears', 'i dont know why i run away', 'save', 'i saw you dancin in a crowded room you look so happy when i\'m not with you, i don\'t know why i run away, oo girl, i make you cry, i run away, take me back, cuz i wanna stay, save your tears for anothe', 'about-bg2.png', '2022-07-25 11:55:29'),
(6, 'Alone again', 'i dont know if i can be alone again', 'alone', 'call me up and i\'ll send for you, take me down to your altitude, i dont know if i can be alone again, i dont know if i can sleep alone again, check my pulse for a second time, i took too much i don\'t ', 'after-hours.png', '2022-07-25 17:22:47');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `contacts`
--
ALTER TABLE `contacts`
  ADD PRIMARY KEY (`serial_number`);

--
-- Indexes for table `posts`
--
ALTER TABLE `posts`
  ADD PRIMARY KEY (`serial_number`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `contacts`
--
ALTER TABLE `contacts`
  MODIFY `serial_number` int(50) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `posts`
--
ALTER TABLE `posts`
  MODIFY `serial_number` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
