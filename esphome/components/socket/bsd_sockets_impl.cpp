#include "socket.h"
#include "esphome/core/defines.h"
#include "esphome/core/helpers.h"

#ifdef USE_SOCKET_IMPL_BSD_SOCKETS

#include <cstring>

#ifdef USE_ESP32
#include <esp_idf_version.h>
#include <lwip/sockets.h>
#endif

#ifdef USE_ZEPHYR
#include <net/socket.h>
#define 	MSG_MORE   0x8000
#endif
/*
#include <posix/sys/ioctl.h>
#include <posix/unistd.h>
*/

namespace esphome {
namespace socket {

std::string format_sockaddr(const struct sockaddr_storage &storage) {
  if (storage.ss_family == AF_INET) {
    const struct sockaddr_in *addr = reinterpret_cast<const struct sockaddr_in *>(&storage);
    char buf[INET_ADDRSTRLEN];
#ifdef USE_ZEPHY
    const char *ret = zsock_inet_ntop(AF_INET, &addr->sin_addr, buf, sizeof(buf));
#else
    const char *ret = inet_ntop(AF_INET, &addr->sin_addr, buf, sizeof(buf));
#endif
    if (ret == nullptr)
      return {};
    return std::string{buf};
  } else if (storage.ss_family == AF_INET6) {
    const struct sockaddr_in6 *addr = reinterpret_cast<const struct sockaddr_in6 *>(&storage);
    char buf[INET6_ADDRSTRLEN];
#ifdef USE_ZEPHY
    const char *ret = zsock_inet_ntop(AF_INET, &addr->sin_addr, buf, sizeof(buf));
#else
    const char *ret = inet_ntop(AF_INET6, &addr->sin6_addr, buf, sizeof(buf));
#endif
    if (ret == nullptr)
      return {};
    return std::string{buf};
  }
  return {};
}

class BSDSocketImpl : public Socket {
 public:
  BSDSocketImpl(int fd) : Socket(), fd_(fd) {}
  ~BSDSocketImpl() override {
    if (!closed_) {
      close();  // NOLINT(clang-analyzer-optin.cplusplus.VirtualCall)
    }
  }
  std::unique_ptr<Socket> accept(struct sockaddr *addr, socklen_t *addrlen) override {
#ifdef USE_ZEPHYR
    int fd = zsock_accept(fd_, addr, addrlen);
#else
    int fd = ::accept(fd_, addr, addrlen);
#endif
    if (fd == -1)
      return {};
    return make_unique<BSDSocketImpl>(fd);
  }
  int bind(const struct sockaddr *addr, socklen_t addrlen) override {
#ifdef USE_ZEPHYR
    return zsock_bind(fd_, addr, addrlen);
#else
    return ::bind(fd_, addr, addrlen);
#endif
  }
  int close() override {
#ifdef USE_ZEPHYR
    int ret = zsock_close(fd_);
#else
    int ret = ::close(fd_);
#endif
    closed_ = true;
    return ret;
  }
  int shutdown(int how) override { return ::shutdown(fd_, how); }

  int getpeername(struct sockaddr *addr, socklen_t *addrlen) override {
#ifdef USE_ZEPHYR
    return -1;
#else
    return ::getpeername(fd_, addr, addrlen);
#endif
  }

  std::string getpeername() override {
#ifdef USE_ZEPHYR
    return std::string("ZEPHYR_NOT_IMPLEMENTED");
#else
    struct sockaddr_storage storage;
    socklen_t len = sizeof(storage);
    int err = this->getpeername((struct sockaddr *) &storage, &len);
    if (err != 0)
      return {};
    return format_sockaddr(storage);
  #endif
  }

  int getsockname(struct sockaddr *addr, socklen_t *addrlen) override {
#ifdef USE_ZEPHYR
    return zsock_getsockname(fd_, addr, addrlen);
#else
    return ::getsockname(fd_, addr, addrlen);
#endif
  }

  std::string getsockname() override {
    struct sockaddr_storage storage;
    socklen_t len = sizeof(storage);
    int err = this->getsockname((struct sockaddr *) &storage, &len);
    if (err != 0)
      return {};
    return format_sockaddr(storage);
  }
  int getsockopt(int level, int optname, void *optval, socklen_t *optlen) override {
#ifdef USE_ZEPHYR
    return zsock_getsockopt(fd_, level, optname, optval, optlen);
#else
    return ::getsockopt(fd_, level, optname, optval, optlen);
#endif
  }

  int setsockopt(int level, int optname, const void *optval, socklen_t optlen) override {
#ifdef USE_ZEPHYR
    return zsock_setsockopt(fd_, level, optname, optval, optlen);
#else
    return ::setsockopt(fd_, level, optname, optval, optlen);
#endif
  }
  int listen(int backlog) override {
#ifdef USE_ZEPHYR
    return zsock_listen(fd_, backlog);
#else
    return ::listen(fd_, backlog);
#endif
  }
  ssize_t read(void *buf, size_t len) override {
#ifdef USE_ZEPHYR
    return zsock_recv(fd_, buf, len, 0);
#else
    return ::read(fd_, buf, len);
#endif
  }
  ssize_t readv(const struct iovec *iov, int iovcnt) override {
#if (defined(USE_ESP32) && ESP_IDF_VERSION_MAJOR < 4) || defined(USE_ZEPHYR)
    // esp-idf v3 doesn't have readv, emulate it
    ssize_t ret = 0;
    for (int i = 0; i < iovcnt; i++) {
      ssize_t err = this->read(reinterpret_cast<uint8_t *>(iov[i].iov_base), iov[i].iov_len);
      if (err == -1) {
        if (ret != 0)
          // if we already read some don't return an error
          break;
        return err;
      }
      ret += err;
      if (err != iov[i].iov_len)
        break;
    }
    return ret;
#elif defined(USE_ESP32)
    // ESP-IDF v4 only has symbol lwip_readv
    return ::lwip_readv(fd_, iov, iovcnt);
#else
    return ::readv(fd_, iov, iovcnt);
#endif
  }
  ssize_t write(const void *buf, size_t len) override {
#ifdef USE_ZEPHYR
    return zsock_send(fd_, buf, len, 0);
#else
    return ::write(fd_, buf, len);
#endif
  }
  ssize_t send(void *buf, size_t len, int flags) {
#ifdef USE_ZEPHYR
    return zsock_send(fd_, buf, len, flags);
#else
    return ::send(fd_, buf, len, flags);
#endif
  }
  ssize_t writev(const struct iovec *iov, int iovcnt) override {
#if (defined(USE_ESP32) && ESP_IDF_VERSION_MAJOR < 4) || defined(USE_ZEPHYR)
    // esp-idf v3 doesn't have writev, emulate it
    ssize_t ret = 0;
    for (int i = 0; i < iovcnt; i++) {
      ssize_t err =
          this->send(reinterpret_cast<uint8_t *>(iov[i].iov_base), iov[i].iov_len, i == iovcnt - 1 ? 0 : MSG_MORE);
      if (err == -1) {
        if (ret != 0)
          // if we already wrote some don't return an error
          break;
        return err;
      }
      ret += err;
      if (err != iov[i].iov_len)
        break;
    }
    return ret;
#elif defined(USE_ESP32)
    // ESP-IDF v4 only has symbol lwip_writev
    return ::lwip_writev(fd_, iov, iovcnt);
#else
    return ::writev(fd_, iov, iovcnt);
#endif
  }
  int setblocking(bool blocking) override {
#ifdef USE_ZEPHYR
    int fl = zsock_fcntl(fd_, F_GETFL, 0);
#else
    int fl = ::fcntl(fd_, F_GETFL, 0);
#endif
    if (blocking) {
      fl &= ~O_NONBLOCK;
    } else {
      fl |= O_NONBLOCK;
    }
#ifdef USE_ZEPHYR
    zsock_fcntl(fd_, F_SETFL, fl);
#else
    ::fcntl(fd_, F_SETFL, fl);
#endif
    return 0;
  }

 protected:
  int fd_;
  bool closed_ = false;
};

std::unique_ptr<Socket> socket(int domain, int type, int protocol) {
  int ret = ::socket(domain, type, protocol);
  if (ret == -1)
    return nullptr;
  return std::unique_ptr<Socket>{new BSDSocketImpl(ret)};
}

}  // namespace socket
}  // namespace esphome

#endif  // USE_SOCKET_IMPL_BSD_SOCKETS
